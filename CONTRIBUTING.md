# Contributing to Whisper-Hindi2Hinglish + Video-to-SRT

Thank you for your interest in contributing! 🎉

## Fork Attribution

This project is a **fork** of [OriserveAI/Whisper-Hindi2Hinglish](https://github.com/OriserveAI/Whisper-Hindi2Hinglish).

### What to Contribute Here

Contributions are welcome for:
- ✅ Video-to-SRT feature improvements
- ✅ Bug fixes in web server or SRT generation
- ✅ Documentation enhancements
- ✅ Additional video format support
- ✅ Web UI improvements
- ✅ Docker/deployment enhancements
- ✅ Test coverage improvements

### What to Contribute Upstream

For improvements to the **core streaming functionality** (WebSocket server, models, VAD), please contribute to the [upstream repository](https://github.com/OriserveAI/Whisper-Hindi2Hinglish).

---

## Getting Started

### 1. Fork and Clone

```bash
# Fork this repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/Whisper-Hindi2Hinglish.git
cd Whisper-Hindi2Hinglish

# Add upstream remote
git remote add upstream https://github.com/sanjogbora/Whisper-Hindi2Hinglish.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (including dev dependencies)
pip install -r requirements-dev.txt

# Verify installation
python -m pytest tests/
```

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

---

## Development Guidelines

### Code Style

We follow PEP 8 style guidelines:

```bash
# Format code with Black
black .

# Check for issues with flake8
flake8 .
```

### Testing

- Add tests for new features in `tests/`
- Ensure all tests pass before submitting:

```bash
pytest tests/
```

### Documentation

- Update relevant documentation in `docs/` for new features
- Update README.md if user-facing changes
- Add docstrings to new functions/classes

---

## Submitting Changes

### 1. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add feature: video batch processing"
```

**Commit Message Format:**
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues if applicable: "Fix #123: Handle empty audio"

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to your fork on GitHub
2. Click "Pull Request"
3. Select your feature branch
4. Fill out the PR template:
   - **Description**: What does this PR do?
   - **Related Issue**: Link to issue if applicable
   - **Testing**: How did you test this?
   - **Screenshots**: If UI changes

---

## Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows PEP 8 style guidelines
- [ ] All tests pass (`pytest tests/`)
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts with main branch

---

## Reporting Issues

### Bug Reports

Please include:
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Minimal steps to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, GPU/CPU
- **Logs**: Relevant error messages or logs

### Feature Requests

Please include:
- **Description**: Clear description of the feature
- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How might this work?
- **Alternatives**: Other approaches considered?

---

## Development Setup (Detailed)

### Prerequisites

- Python 3.10+
- FFmpeg installed
- Git

### Full Setup

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/Whisper-Hindi2Hinglish.git
cd Whisper-Hindi2Hinglish

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .

# Verify CLI commands work
whisper-srt --help
whisper-web --help
whisper-ws --help

# Run tests
pytest tests/
```

### Running Locally

**Web Server:**
```bash
python web_server.py
# Open: http://localhost:5000
```

**WebSocket Server:**
```bash
# Terminal 1
python websocket_server.py

# Terminal 2
python client_file.py --wav-path examples/example.wav
```

---

## Code of Conduct

Please be respectful and professional in all interactions. We're here to build something useful together!

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Unacceptable Behavior

- Trolling, insults, or derogatory comments
- Harassment of any kind
- Publishing private information
- Other unprofessional conduct

---

## Questions?

- **General questions**: [Open a discussion](https://github.com/sanjogbora/Whisper-Hindi2Hinglish/discussions)
- **Bug reports**: [Open an issue](https://github.com/sanjogbora/Whisper-Hindi2Hinglish/issues)
- **Feature requests**: [Open an issue](https://github.com/sanjogbora/Whisper-Hindi2Hinglish/issues)

---

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

Thank you for contributing! 🙏
