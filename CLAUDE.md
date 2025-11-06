# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PensanTalk is a text-to-speech application built with Python using the pyttsx3 library. This project converts text input into spoken audio output.

## Development Commands

### Running the Application
```bash
python3 main.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Running Tests
```bash
pytest
pytest tests/test_specific.py  # Run specific test file
pytest tests/test_specific.py::test_function  # Run specific test
```

## Architecture

### Core Components

**pyttsx3 Integration**: The project uses pyttsx3 as the primary TTS engine, which supports multiple TTS engines:
- `sapi5` on Windows
- `nsss` on macOS
- `espeak` on Linux

### Key Design Considerations

- **Voice Selection**: pyttsx3 allows switching between available system voices. Consider implementing voice selection functionality.
- **Speech Properties**: Rate, volume, and voice can be configured through the engine's property system.
- **Async Operations**: For GUI applications, pyttsx3's `runAndWait()` blocks execution. Consider using threading or async patterns for responsive UIs.
- **Error Handling**: TTS engines may fail if system dependencies are missing (e.g., espeak on Linux). Implement proper error handling and fallback mechanisms.

## Python-Specific Notes

- Target Python 3.8+ for compatibility
- Use virtual environments (`venv` or `virtualenv`) to isolate dependencies
- pyttsx3 requires platform-specific system dependencies:
  - Linux: `espeak` or `espeak-ng` package
  - macOS: Built-in NSSpeechSynthesizer
  - Windows: Built-in SAPI5
