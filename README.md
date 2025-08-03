# TTS Package

An independent Text-to-Speech (TTS) package extracted from GLaDOS, providing GLaDOS and Kokoro voice synthesis capabilities.

## Features

- **GLaDOS Voice**: High-quality GLaDOS voice synthesis using VITS model
- **Kokoro Voices**: Multiple voice options with Kokoro TTS engine
- **Protocol-based Interface**: Clean, extensible API for TTS synthesis
- **ONNX Runtime**: Optimized inference with ONNX models

## Installation

Install the package using uv:

```bash
# For CPU inference
uv add tts-package[cpu]

# For CUDA GPU inference
uv add tts-package[cuda]
```

## Quick Start

```python
from glados_tts import get_speech_synthesizer
import soundfile as sf

# Use GLaDOS voice
synthesizer = get_speech_synthesizer("glados")
audio = synthesizer.generate_speech_audio("Hello, this is GLaDOS speaking.")
sf.write("glados_output.wav", audio, synthesizer.sample_rate)

# Use Kokoro voice
from glados_tts.synthesizers.tts_kokoro import get_voices
print("Available voices:", get_voices())

kokoro_synth = get_speech_synthesizer("af_alloy")  # or any available voice
audio = kokoro_synth.generate_speech_audio("Hello from Kokoro!")
sf.write("kokoro_output.wav", audio, kokoro_synth.sample_rate)
```

## API Reference

### `get_speech_synthesizer(voice: str = "glados")`

Factory function to create TTS synthesizer instances.

**Parameters:**
- `voice`: Voice name ("glados" for GLaDOS voice, or any Kokoro voice name)

**Returns:**
- `SpeechSynthesizerProtocol`: TTS synthesizer instance

### `SpeechSynthesizerProtocol`

Protocol defining the TTS interface.

**Attributes:**
- `sample_rate: int`: Audio sample rate

**Methods:**
- `generate_speech_audio(text: str) -> NDArray[np.float32]`: Convert text to audio

## Development

```bash
# Install in development mode
uv add -e .[dev]

# Run linting
uv run ruff check .

# Run type checking
uv run mypy .

# Run tests
uv run pytest
```

## License

This package is extracted from the GLaDOS project and inherits its licensing terms.