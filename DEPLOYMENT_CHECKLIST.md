# Deployment Checklist

Complete checklist for deploying the Whisper-Hindi2Hinglish Video Caption Editor to production.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deployment Steps](#deployment-steps)
3. [Post-Deployment Verification](#post-deployment-verification)
4. [Monitoring & Maintenance](#monitoring--maintenance)
5. [Rollback Procedure](#rollback-procedure)
6. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Environment Setup

- [ ] **Python Environment**
  - [ ] Python 3.10 or newer installed
  - [ ] Virtual environment created (`python -m venv venv`)
  - [ ] Virtual environment activated
  - [ ] Pip upgraded (`pip install --upgrade pip`)

- [ ] **System Dependencies**
  - [ ] FFmpeg installed and accessible in PATH
  - [ ] Verify FFmpeg: `ffmpeg -version`
  - [ ] CUDA drivers installed (if using GPU)
  - [ ] Verify CUDA: `nvidia-smi` (GPU only)

- [ ] **Directory Structure**
  - [ ] Project directory created
  - [ ] `templates/` directory exists with `editor.html`
  - [ ] `tests/` directory exists
  - [ ] `docs/` directory exists
  - [ ] `presets/` directory exists (optional, can be empty)
  - [ ] `fonts/` directory exists (optional, can be empty)
  - [ ] `sessions/` directory exists or will be auto-created
  - [ ] Write permissions on all directories

### Configuration

- [ ] **Application Configuration**
  - [ ] `UPLOAD_FOLDER` configured (default: `~/Downloads`)
  - [ ] `MAX_FILE_SIZE` configured (default: 500MB)
  - [ ] Server port configured (default: 5000)
  - [ ] Host address configured (default: 0.0.0.0 for production)

- [ ] **Environment Variables** (if applicable)
  - [ ] `FLASK_ENV` set to `production`
  - [ ] `FLASK_DEBUG` set to `0` or `False`
  - [ ] Custom UPLOAD_FOLDER path set (if needed)
  - [ ] Custom port set (if needed)

### Dependencies Installation

- [ ] **Install Requirements**
  ```bash
  pip install -r requirements.txt
  ```
  - [ ] All requirements installed without errors
  - [ ] Verify critical imports: `python -c "import flask, torch, whisper_timestamped"`

- [ ] **Optional: GPU Support**
  ```bash
  pip install -r requirements-cuda.txt
  ```
  - [ ] CUDA packages installed (if using GPU)

### Code & Testing

- [ ] **Run Final Validation**
  ```bash
  python tests/final_validation.py
  ```
  - [ ] All critical checks pass
  - [ ] Deployment readiness confirmed

- [ ] **Run Test Suite**
  ```bash
  python -m pytest tests/ -v
  ```
  - [ ] All tests pass (or acceptable failures documented)
  - [ ] Unit tests pass
  - [ ] Integration tests pass
  - [ ] E2E tests pass

- [ ] **Code Quality**
  - [ ] No syntax errors
  - [ ] No TODO/FIXME for critical issues
  - [ ] No debug prints in production code
  - [ ] Type hints complete (optional but recommended)

### Security Review

- [ ] **Security Checks**
  - [ ] Path traversal protection in place (`is_safe_path`)
  - [ ] Input validation implemented
  - [ ] File upload limits enforced
  - [ ] CORS configured appropriately
  - [ ] Error messages don't leak sensitive info
  - [ ] No hardcoded secrets or passwords
  - [ ] Secure filename handling

### Backup

- [ ] **Pre-Deployment Backup**
  - [ ] Current deployment backed up (if updating)
  - [ ] Database backed up (if using external database)
  - [ ] Configuration files backed up
  - [ ] Custom presets and fonts backed up

---

## Deployment Steps

### Step 1: Deploy Files

- [ ] **Copy Files to Server**
  ```bash
  # Option A: Using rsync
  rsync -avz --exclude 'venv' --exclude '__pycache__' \
         --exclude '*.pyc' --exclude '.git' \
     /local/path/Whisper-Hindi2Hinglish/ user@server:/deploy/path/

  # Option B: Using git (recommended)
  git clone <repository-url> /deploy/path/
  cd /deploy/path/
  git checkout <branch-or-tag>
  ```

- [ ] **Set Permissions**
  ```bash
  chmod -R 755 /deploy/path/
  chmod +x /deploy/path/*.sh  # Make shell scripts executable
  ```

### Step 2: Install Dependencies

- [ ] **Create Virtual Environment**
  ```bash
  cd /deploy/path/
  python3 -m venv venv
  source venv/bin/activate  # On Linux/Mac
  # or
  venv\Scripts\activate  # On Windows
  ```

- [ ] **Install Python Packages**
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- [ ] **Verify Installation**
  ```bash
  python -c "import flask, torch, whisper_timestamped; print('All imports OK')"
  ```

### Step 3: Configure Application

- [ ] **Review Configuration**
  - [ ] Check `web_server.py` configuration
  - [ ] Set appropriate `UPLOAD_FOLDER`
  - [ ] Set appropriate `MAX_FILE_SIZE`
  - [ ] Configure server host and port

- [ ] **Set Environment Variables** (if using)
  ```bash
  export FLASK_ENV=production
  export FLASK_DEBUG=0
  # Add any custom environment variables
  ```

### Step 4: Create Required Directories

- [ ] **Create Runtime Directories**
  ```bash
  mkdir -p /deploy/path/sessions
  mkdir -p /deploy/path/presets
  mkdir -p /deploy/path/fonts
  mkdir -p /deploy/path/temp  # For temporary files
  ```

- [ ] **Set Directory Permissions**
  ```bash
  chmod 755 /deploy/path/sessions
  chmod 755 /deploy/path/presets
  chmod 755 /deploy/path/fonts
  chmod 755 /deploy/path/temp
  ```

### Step 5: Run Validation

- [ ] **Run Final Validation Script**
  ```bash
  python tests/final_validation.py
  ```
  - [ ] All checks pass
  - [ ] Deployment readiness confirmed

- [ ] **Manual Smoke Tests**
  ```bash
  # Test import
  python -c "from session_manager import SessionManager; print('OK')"

  # Test preset manager
  python -c "from caption_styling import PresetManager; print('OK')"

  # Test pipeline
  python -c "from video_caption_pipeline import VideoCaptionPipeline; print('OK')"
  ```

### Step 6: Start Server

- [ ] **Start Server (Development/Testing)**
  ```bash
  python web_server.py --port 5000
  ```

- [ ] **Start Server (Production - using Gunicorn)**
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 web_server:app
  ```

- [ ] **Start Server (Production - using systemd service)**
  ```bash
  # Create service file at /etc/systemd/system/whisper-editor.service
  sudo systemctl daemon-reload
  sudo systemctl enable whisper-editor
  sudo systemctl start whisper-editor
  ```

### Step 7: Verify Server

- [ ] **Check Server Logs**
  - [ ] No error messages in logs
  - [ ] Server started successfully
  - [ ] All modules loaded correctly

- [ ] **Test Basic Endpoints**
  ```bash
  # Health check
  curl http://localhost:5000/health

  # API status
  curl http://localhost:5000/api/status

  # Check API docs
  curl http://localhost:5000/api
  ```

---

## Post-Deployment Verification

### Functional Testing

- [ ] **Test Session Creation**
  ```bash
  curl -X POST http://localhost:5000/api/sessions \
    -H "Content-Type: application/json" \
    -d '{"video_path": "/path/to/video.mp4"}'
  ```

- [ ] **Test Session Retrieval**
  ```bash
  curl http://localhost:5000/api/sessions/<session-id>
  ```

- [ ] **Test Style Application**
  ```bash
  curl -X PUT http://localhost:5000/api/sessions/<session-id>/style \
    -H "Content-Type: application/json" \
    -d '{"preset_name": "reels_standard"}'
  ```

- [ ] **Test Preview Generation**
  ```bash
  curl http://localhost:5000/api/sessions/<session-id>/preview
  ```

- [ ] **Test Preset List**
  ```bash
  curl http://localhost:5000/api/presets
  ```

- [ ] **Test Font List**
  ```bash
  curl http://localhost:5000/api/fonts
  ```

### Editor Interface Testing

- [ ] **Test Editor Page**
  - [ ] Navigate to `http://localhost:5000/editor/new`
  - [ ] Page loads without errors
  - [ ] Video player displays
  - [ ] Style controls visible
  - [ ] No JavaScript errors in console

- [ ] **Test Complete Workflow**
  - [ ] Upload a test video
  - [ ] Generate captions
  - [ ] Apply a style preset
  - [ ] Preview captions
  - [ ] Download captioned video

### Performance Testing

- [ ] **Load Testing**
  - [ ] Test with multiple concurrent users
  - [ ] Test with large video files (100MB+)
  - [ ] Monitor memory usage
  - [ ] Monitor CPU usage
  - [ ] Monitor response times

- [ ] **Stress Testing**
  - [ ] Test with maximum file size (500MB)
  - [ ] Test with rapid sequential requests
  - [ ] Verify no memory leaks
  - [ ] Verify no connection drops

### Security Testing

- [ ] **Input Validation**
  - [ ] Test with malicious file uploads
  - [ ] Test with path traversal attempts
  - [ ] Test with oversized requests
  - [ ] Test with invalid JSON

- [ ] **Access Control**
  - [ ] Verify CORS settings
  - [ ] Test unauthorized access attempts
  - [ ] Verify error messages don't leak info

---

## Monitoring & Maintenance

### Monitoring Setup

- [ ] **Application Monitoring**
  - [ ] Set up log monitoring
  - [ ] Set up error tracking (e.g., Sentry)
  - [ ] Set up performance monitoring
  - [ ] Set up uptime monitoring

- [ ] **Resource Monitoring**
  - [ ] Monitor CPU usage
  - [ ] Monitor memory usage
  - [ ] Monitor disk space
  - [ ] Monitor network traffic

- [ ] **Business Metrics**
  - [ ] Track number of sessions created
  - [ ] Track processing times
  - [ ] Track error rates
  - [ ] Track user activity

### Maintenance Tasks

- [ ] **Regular Cleanup**
  - [ ] Clean up old sessions (automated via SessionManager)
  - [ ] Clean up temporary files
  - [ ] Clean up logs
  - [ ] Free disk space

- [ ] **Updates & Patches**
  - [ ] Monitor for security updates
  - [ ] Update Python packages regularly
  - [ ] Update FFmpeg if needed
  - [ ] Update system dependencies

- [ ] **Backup Strategy**
  - [ ] Regular backups of custom presets
  - [ ] Regular backups of custom fonts
  - [ ] Regular backups of configuration
  - [ ] Test restore procedures

### Log Management

- [ ] **Log Configuration**
  - [ ] Configure log levels appropriately
  - [ ] Set up log rotation
  - [ ] Configure log retention policy
  - [ ] Set up centralized logging (optional)

- [ ] **Key Logs to Monitor**
  - [ ] Application errors
  - [ ] Failed API requests
  - [ ] Long-running operations
  - [ ] Resource exhaustion warnings

---

## Rollback Procedure

### When to Rollback

- [ ] Critical bugs discovered
- [ ] Security vulnerabilities found
- [ ] Performance degradation
- [ ] Data corruption issues
- [ ] Feature breakage

### Rollback Steps

- [ ] **Stop Current Deployment**
  ```bash
  # If using systemd
  sudo systemctl stop whisper-editor

  # If using Gunicorn directly
  pkill -f gunicorn
  ```

- [ ] **Restore Previous Version**
  ```bash
  # Option A: Using git
  git checkout <previous-commit-or-tag>

  # Option B: Using backup
  cp -r /backup/path/Whisper-Hindi2Hinglish/* /deploy/path/
  ```

- [ ] **Reinstall Dependencies** (if needed)
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```

- [ ] **Restore Configuration**
  ```bash
  # Restore config files from backup
  cp /backup/config/web_server.py /deploy/path/
  cp /backup/config/*.json /deploy/path/
  ```

- [ ] **Restart Server**
  ```bash
  # If using systemd
  sudo systemctl start whisper-editor

  # If using Gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 web_server:app
  ```

- [ ] **Verify Rollback**
  - [ ] Server starts successfully
  - [ ] All endpoints working
  - [ ] No errors in logs
  - [ ] Basic functionality tested

### Rollback Verification

- [ ] **Smoke Tests**
  - [ ] Health check endpoint works
  - [ ] Can create a session
  - [ ] Can retrieve a session
  - [ ] Can apply styles

- [ ] **User Testing**
  - [ ] Test complete workflow
  - [ ] Verify no data loss
  - [ ] Verify performance acceptable

---

## Troubleshooting

### Common Issues

#### Server Won't Start

**Symptoms:** Server fails to start, error on startup

**Possible Causes:**
- Port already in use
- Missing dependencies
- Configuration errors
- Permission issues

**Solutions:**
```bash
# Check port usage
netstat -tlnp | grep :5000
lsof -i :5000

# Try different port
python web_server.py --port 5001

# Check dependencies
pip install -r requirements.txt

# Check logs
tail -f /var/log/whisper-editor.log
```

#### Import Errors

**Symptoms:** ModuleNotFoundError or ImportError

**Possible Causes:**
- Virtual environment not activated
- Dependencies not installed
- PYTHONPATH issues

**Solutions:**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Check PYTHONPATH
echo $PYTHONPATH
export PYTHONPATH=/deploy/path:$PYTHONPATH
```

#### FFmpeg Not Found

**Symptoms:** FFmpeg errors, video processing fails

**Possible Causes:**
- FFmpeg not installed
- FFmpeg not in PATH

**Solutions:**
```bash
# Install FFmpeg
sudo apt install ffmpeg           # Ubuntu/Debian
sudo yum install ffmpeg           # CentOS/RHEL
brew install ffmpeg               # Mac
winget install ffmpeg             # Windows

# Verify installation
ffmpeg -version

# Add to PATH if needed
export PATH=/path/to/ffmpeg:$PATH
```

#### CUDA/GPU Errors

**Symptoms:** CUDA errors, falling back to CPU

**Possible Causes:**
- CUDA not installed
- Wrong CUDA version
- GPU drivers outdated

**Solutions:**
```bash
# Check CUDA installation
nvidia-smi

# Install CUDA (if needed)
# Follow NVIDIA documentation

# Use CPU version if GPU not available
# No action needed - automatic fallback
```

#### Out of Memory

**Symptoms:** Memory errors, process killed

**Possible Causes:**
- Video too large
- Too many concurrent users
- Memory leak

**Solutions:**
```bash
# Reduce MAX_FILE_SIZE in web_server.py

# Increase system swap
sudo swapon /swapfile

# Monitor memory usage
free -h
top

# Restart server regularly (systemd service recommended)
```

#### Permission Errors

**Symptoms:** Permission denied when writing files

**Possible Causes:**
- Insufficient directory permissions
- Wrong file ownership

**Solutions:**
```bash
# Fix directory permissions
chmod 755 /deploy/path/sessions
chmod 755 /deploy/path/temp

# Fix ownership if needed
sudo chown -R user:group /deploy/path/
```

### Getting Help

If issues persist:

1. **Check Logs**
   ```bash
   tail -f /var/log/whisper-editor.log
   ```

2. **Run Diagnostics**
   ```bash
   python tests/final_validation.py
   ```

3. **Review Documentation**
   - README.md
   - USER_GUIDE.md
   - docs/API_REFERENCE.md

4. **Check GitHub Issues**
   - Search for similar issues
   - Report new issue with details

---

## Deployment Summary

### Quick Reference

| Command | Purpose |
|---------|---------|
| `python tests/final_validation.py` | Run pre-deployment validation |
| `pip install -r requirements.txt` | Install dependencies |
| `python web_server.py` | Start development server |
| `gunicorn -w 4 -b 0.0.0.0:5000 web_server:app` | Start production server |
| `curl http://localhost:5000/health` | Health check |

### Critical Files

| File | Purpose |
|------|---------|
| `web_server.py` | Main Flask application |
| `session_manager.py` | Session management |
| `caption_styling.py` | Style presets |
| `video_caption_pipeline.py` | Video embedding |
| `requirements.txt` | Python dependencies |
| `tests/final_validation.py` | Validation script |

### Critical Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/health` | Health check |
| `/api/status` | API status |
| `/api/sessions` | Session CRUD |
| `/api/sessions/{id}/style` | Apply styles |
| `/api/sessions/{id}/preview` | Generate preview |
| `/api/presets` | List presets |

---

**Deployment Checklist Version:** 1.0
**Last Updated:** 2025-02-11
**Project:** Whisper-Hindi2Hinglish Video Caption Editor