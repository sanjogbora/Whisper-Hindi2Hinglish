"""
Flask API Server for Video to SRT Conversion
Upload video and get SRT file back
"""
import argparse
import os
import tempfile
from pathlib import Path

import torch
from flask import Flask, request, send_file, jsonify, render_template
from werkzeug.utils import secure_filename

from logger import logger
from utils import torch_dtype_from_str
from video_to_srt import video_to_srt

app = Flask(__name__, template_folder='templates')

# Configuration
UPLOAD_FOLDER = str(Path.home() / "Downloads")
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'm4v'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Global model config
MODEL_CONFIG = {
    'model_id': 'Oriserve/Whisper-Hindi2Hinglish-Swift',
    'device': 'cuda',
    'dtype': torch.float16
}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with web interface"""
    return render_template('upload.html')


@app.route('/api')
def api_info():
    """API documentation"""
    return jsonify({
        'service': 'Video to SRT Converter',
        'description': 'Upload Hindi-English mixed video and get Roman English SRT subtitles',
        'endpoints': {
            '/upload': {
                'method': 'POST',
                'description': 'Upload video file',
                'parameters': {
                    'video': 'Video file (mp4, avi, mov, mkv, webm, flv, wmv, m4v)',
                    'model': 'Optional: swift (default) or prime'
                },
                'returns': 'SRT file download'
            },
            '/health': {
                'method': 'GET',
                'description': 'Check server health'
            }
        },
        'max_file_size': '500MB',
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model': MODEL_CONFIG['model_id']})


@app.route('/upload', methods=['POST'])
def upload_video():
    """
    Upload video and get SRT file
    """
    # Check if file is present
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    # Get model preference
    model_choice = request.form.get('model', 'swift').lower()
    if model_choice == 'prime':
        model_id = 'Oriserve/Whisper-Hindi2Hinglish-Prime'
    else:
        model_id = 'Oriserve/Whisper-Hindi2Hinglish-Swift'
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(video_path)

    try:
        # Generate SRT file
        logger.info(f"Original filename: {file.filename}")
        logger.info(f"Secured filename: {filename}")
        logger.info(f"Processing video: {filename}")
        srt_filename = Path(filename).stem + '.srt'
        srt_path = os.path.join(app.config['UPLOAD_FOLDER'], srt_filename)
        logger.info(f"SRT filename: {srt_filename}")
        logger.info(f"SRT path: {srt_path}")
        
        video_to_srt(
            video_path,
            srt_path,
            model_id,
            MODEL_CONFIG['device'],
            MODEL_CONFIG['dtype']
        )
        
        # Send SRT file
        return send_file(
            srt_path,
            as_attachment=True,
            download_name=srt_filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(srt_path):
            # Give time for file to be sent before deletion
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video to SRT API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')
    parser.add_argument(
        '--model-id',
        default='Oriserve/Whisper-Hindi2Hinglish-Swift',
        help='Default model ID'
    )
    parser.add_argument('--device', default='cuda', help='Device to run model on')
    parser.add_argument('--dtype', default='float16', help='Data type for model')
    
    args = parser.parse_args()
    
    # Update global config
    MODEL_CONFIG['model_id'] = args.model_id
    MODEL_CONFIG['device'] = args.device
    MODEL_CONFIG['dtype'] = torch_dtype_from_str(args.dtype, args.device)
    
    logger.info(f"Starting API server on http://{args.host}:{args.port}")
    logger.info(f"Using model: {MODEL_CONFIG['model_id']}")
    
    app.run(host=args.host, port=args.port, debug=False)
