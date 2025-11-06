#!/usr/bin/env python3
"""
PensanTalk - Simple Text-to-Speech Converter
Automatically converts markdown files to audio (Mexican Spanish, mono OGG)

Usage: python3 pensantalk.py
"""

import os
import sys
import re
import subprocess
import asyncio
from pathlib import Path
from glob import glob


# Auto-detect and use virtual environment
def ensure_venv():
    """Automatically detect and use venv if not already active"""
    # Check if we're already in a venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return  # Already in venv

    # Look for venv in current directory
    venv_python = None
    for venv_name in ['venv', '.venv', 'env']:
        venv_path = Path(venv_name) / 'bin' / 'python3'
        if venv_path.exists():
            venv_python = str(venv_path)
            break

    if venv_python:
        # Re-execute this script with venv Python
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        print("Warning: No virtual environment found (venv/). Dependencies may not be available.")


# Run venv check before imports
ensure_venv()


# Configuration
VOICE = "es-MX-DaliaNeural"  # Mexican Spanish voice
BITRATE = "48k"              # Audio quality for OGG
IGNORE_FILES = {"CLAUDE.md", "README.md"}


def strip_markdown(text):
    """Remove markdown formatting for cleaner TTS output"""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


async def generate_audio_edge(text, output_file, voice):
    """Generate audio using Edge TTS"""
    try:
        import edge_tts
    except ImportError:
        print("Error: edge-tts not installed. Run: pip install edge-tts")
        sys.exit(1)

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)


def convert_to_ogg(mp3_file, ogg_file, bitrate):
    """Convert MP3 to mono OGG/Opus using ffmpeg"""
    cmd = [
        'ffmpeg', '-i', mp3_file,
        '-ac', '1',                    # Mono
        '-c:a', 'libopus',             # Opus codec
        '-b:a', bitrate,               # Bitrate
        ogg_file,
        '-y'                           # Overwrite
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error converting to OGG: {result.stderr}")
        sys.exit(1)


def find_markdown_files():
    """Find all .md files in current directory, excluding special files"""
    md_files = []
    for file in glob("*.md"):
        if file not in IGNORE_FILES:
            md_files.append(file)
    return sorted(md_files)


def select_file(files):
    """Let user select a file from a list"""
    print(f"\nFound {len(files)} markdown file(s):")
    for i, file in enumerate(files, 1):
        print(f"  [{i}] {file}")

    while True:
        try:
            choice = input(f"\nSelect file (1-{len(files)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                return files[idx]
            else:
                print(f"Please enter a number between 1 and {len(files)}")
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(0)


def get_file_duration(file_path):
    """Get audio file duration using ffprobe"""
    cmd = ['ffprobe', '-hide_banner', file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    for line in result.stderr.split('\n'):
        if 'Duration:' in line:
            duration = line.split('Duration:')[1].split(',')[0].strip()
            return duration
    return "Unknown"


def process_markdown_file(md_file):
    """Process a single markdown file to audio"""
    print(f"\n📄 Processing: {md_file}")

    # Read and process markdown
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    text = strip_markdown(text)
    print(f"   Text length: {len(text):,} characters")

    # Generate output filenames
    base_name = Path(md_file).stem
    temp_mp3 = f"{base_name}-temp.mp3"
    output_ogg = f"{base_name}.ogg"

    # Generate audio with Edge TTS
    print(f"   Generating speech with Mexican voice...")
    try:
        asyncio.run(generate_audio_edge(text, temp_mp3, VOICE))
    except Exception as e:
        print(f"Error generating audio: {e}")
        sys.exit(1)

    # Convert to mono OGG
    print(f"   Converting to mono OGG/Opus...")
    convert_to_ogg(temp_mp3, output_ogg, BITRATE)

    # Clean up temp file
    try:
        os.remove(temp_mp3)
    except:
        pass

    # Show results
    file_size = os.path.getsize(output_ogg) / (1024 * 1024)  # MB
    duration = get_file_duration(output_ogg)

    print(f"\n✅ Created: {output_ogg}")
    print(f"   Size: {file_size:.1f} MB")
    print(f"   Duration: {duration}")


def main():
    """Main entry point"""
    # Find markdown files
    md_files = find_markdown_files()

    if not md_files:
        print("No markdown files found in current directory.")
        print("(Excluding CLAUDE.md and README.md)")
        sys.exit(1)

    # Select file
    if len(md_files) == 1:
        selected_file = md_files[0]
        print(f"Found: {selected_file}")
    else:
        selected_file = select_file(md_files)

    # Process the file
    process_markdown_file(selected_file)


if __name__ == '__main__':
    main()
