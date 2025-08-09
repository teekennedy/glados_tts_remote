#!/usr/bin/env python3
"""GLaDOS TTS CLI tool for generating speech from text."""

import argparse
import sys
from pathlib import Path


from .synthesizers.tts_glados import SpeechSynthesizer


def say(text: str, output_path: Path) -> None:
    import soundfile as sf

    # Initialize the synthesizer
    synthesizer = SpeechSynthesizer()

    # Generate audio from text
    audio = synthesizer.generate_speech_audio(text)

    # Write to output file
    sf.write(output_path, audio, synthesizer.sample_rate)

    print(f"Generated audio saved to: {output_path}")


def start_server(host: str = "localhost", port: int = 8124) -> None:
    """Start the Piper HTTP server with GLaDOS voice."""
    try:
        from piper.http_server import main as piper_main
    except ImportError:
        print("Error: piper-tts[http] is required for --serve flag")
        print("Install with: uv sync --extra http")
        sys.exit(1)

    # Ensure Piper-compatible voice files exist
    from .utils import resource_path

    glados_onnx = resource_path("glados.onnx")
    glados_json = resource_path("glados.onnx.json")

    if not glados_onnx.exists() or not glados_json.exists():
        print(f"Error: Required GLaDOS model files not found in {glados_onnx.parent}")
        print("Expected: glados.onnx and glados.onnx.json")
        sys.exit(1)

    print(f"Starting GLaDOS TTS server on {host}:{port}")
    print(f"Using model: {glados_onnx}")

    # Configure arguments for Piper server
    sys.argv = [
        "piper-server",
        "--model",
        str(glados_onnx),
        "--host",
        host,
        "--port",
        str(port),
    ]

    # Start Piper server
    piper_main()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate GLaDOS TTS audio from text or start HTTP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Create mutually exclusive group for serve vs generate
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        "--serve",
        action="store_true",
        help="Start HTTP server with GLaDOS voice",
    )

    mode_group.add_argument(
        "--say",
        type=str,
        help="Text to synthesize into speech",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for the generated .wav file (required with --say)",
    )

    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for HTTP server (default: localhost)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8124,
        help="Port for HTTP server (default: 8124)",
    )

    args = parser.parse_args()

    if args.serve:
        start_server(args.host, args.port)
    else:
        # Validate required arguments for speech generation
        if not args.output:
            parser.error("--output is required when using --say")

        say(args.say, args.output)


if __name__ == "__main__":
    main()
