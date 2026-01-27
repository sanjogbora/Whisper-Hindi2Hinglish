from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="whisper-hindi2hinglish-srt",
    version="1.0.0",
    author="Sanjog Bora",
    author_email="",
    description="Video-to-SRT converter for Hindi/Hinglish using Whisper (Fork of OriserveAI/Whisper-Hindi2Hinglish)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sanjogbora/Whisper-Hindi2Hinglish",
    project_urls={
        "Original Repository": "https://github.com/OriserveAI/Whisper-Hindi2Hinglish",
        "Bug Tracker": "https://github.com/sanjogbora/Whisper-Hindi2Hinglish/issues",
        "Documentation": "https://github.com/sanjogbora/Whisper-Hindi2Hinglish/tree/main/docs",
    },
    py_modules=[
        "video_to_srt",
        "websocket_server",
        "web_server",
        "client_file",
        "client_mic",
        "example_api_usage",
        "utils",
        "logger",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.5.1",
        "torchaudio>=2.5.1",
        "torchvision>=0.20.1",
        "transformers>=4.47.1",
        "accelerate>=1.2.1",
        "whisper-timestamped>=1.15.9",
        "webrtcvad==2.0.10",
        "librosa>=0.10.2",
        "numpy>=2.3.5",
        "websockets>=14.1",
        "flask>=3.0.0",
        "werkzeug>=3.0.1",
    ],
    extras_require={
        "microphone": ["pyaudio"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "flake8>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "whisper-srt=video_to_srt:main",
            "whisper-web=web_server:main",
            "whisper-ws=websocket_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "examples/*.wav"],
    },
)
