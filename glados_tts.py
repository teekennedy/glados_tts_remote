#!/usr/bin/env python3
"""GLaDOS TTS CLI tool for generating speech from text."""

import argparse
from pathlib import Path

import soundfile as sf

from glados_tts.synthesizers.tts_glados import SpeechSynthesizer


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate GLaDOS TTS audio from text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--say",
        type=str,
        required=True,
        help="Text to synthesize into speech",
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for the generated .wav file",
    )
    
    args = parser.parse_args()
    
    # Initialize the synthesizer
    synthesizer = SpeechSynthesizer()
    
    # Generate audio from text
    audio = synthesizer.generate_speech_audio(args.say)
    
    # Write to output file
    sf.write(args.output, audio, synthesizer.sample_rate)
    
    print(f"Generated audio saved to: {args.output}")


if __name__ == "__main__":
    main()