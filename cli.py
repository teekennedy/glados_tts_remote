import argparse
import asyncio
import sys
from hashlib import sha256
from pathlib import Path

import httpx
from rich import print as rprint
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn

# Type aliases for clarity
type FileHash = str
type FileURL = str
type FileName = str

# Details of all the models.  Each key is the file path where the model should be saved
MODEL_DETAILS: dict[FileName, dict[FileURL, FileHash]] = {
    "models/TTS/glados.onnx": {
        "url": "https://github.com/dnhkng/GlaDOS/releases/download/0.1/glados.onnx",
        "checksum": "17ea16dd18e1bac343090b8589042b4052f1e5456d42cad8842a4f110de25095",
    },
    "models/TTS/phomenizer_en.onnx": {
        "url": "https://github.com/dnhkng/GlaDOS/releases/download/0.1/phomenizer_en.onnx",
        "checksum": "b64dbbeca8b350927a0b6ca5c4642e0230173034abd0b5bb72c07680d700c5a0",
    },
}


async def download_with_progress(
    client: httpx.AsyncClient,
    url: str,
    file_path: Path,
    expected_checksum: str,
    progress: Progress,
) -> bool:
    """
    Download a single file with progress tracking and SHA-256 checksum verification.

    Returns:
        bool: True if download and verification succeeded, False otherwise
    """
    task_id = progress.add_task(f"Downloading {file_path}", status="")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    hash_sha256 = sha256()

    try:
        async with client.stream("GET", url) as response:
            response.raise_for_status()

            # Set total size for progress bar
            total_size = int(response.headers.get("Content-Length", 0))
            if total_size:
                progress.update(task_id, total=total_size)

            with file_path.open(mode="wb") as f:
                async for chunk in response.aiter_bytes(32768):  # 32KB chunks
                    f.write(chunk)
                    # Update the hash as we go along, for speed
                    hash_sha256.update(chunk)
                    progress.advance(task_id, len(chunk))

        # Verify checksum, and delete failed files
        actual_checksum = hash_sha256.hexdigest()
        if actual_checksum != expected_checksum:
            progress.update(task_id, status="[bold red]Checksum failed")
            Path.unlink(file_path)
            return False
        else:
            progress.update(task_id, status="[bold green]OK")
            return True

    except Exception as e:
        progress.update(task_id, status=f"[bold red]Error: {str(e)}")
        return False


async def download_models() -> int:
    """
    Main async controller for downloading all the specified models:
        - ASR model: nemo-parakeet_tdt_ctc_110m.onnx
        - VAD model: silero_vad.onnx
        - TTS model: glados.onnx
        - Phonemizer model: phomenizer_en.onnx

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    with Progress(
        TextColumn("[grey50][progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TextColumn("  {task.fields[status]}"),
    ) as progress:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Create a download task for each file
            tasks = [
                asyncio.create_task(
                    download_with_progress(
                        client,
                        model_info["url"],
                        Path(path),
                        model_info["checksum"],
                        progress,
                    )
                )
                for path, model_info in MODEL_DETAILS.items()
            ]
            results: list[bool] = await asyncio.gather(*tasks)

    if not all(results):
        rprint("\n[bold red]Some files were not downloaded successfully")
        return 1
    rprint("\n[bold green]All files downloaded and verified successfully")
    return 0


def main() -> int:
    """
    Command-line interface (CLI) entry point for the GLaDOS voice assistant.

    Provides three primary commands:
    - 'download': Download required model files
    - 'start': Launch the GLaDOS voice assistant
    - 'say': Generate speech from input text

    The function sets up argument parsing with optional configuration file paths and handles
    command execution based on user input. If no command is specified, it defaults to starting
    the assistant.

    Optional Arguments:
        --config (str): Path to configuration file, defaults to 'glados_config.yaml'

    Raises:
        SystemExit: If invalid arguments are provided
    """
    parser = argparse.ArgumentParser(description="GLaDOS Voice Assistant")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Download command
    subparsers.add_parser("download", help="Download model files")

    args = parser.parse_args()

    if args.command == "download":
        return asyncio.run(download_models())
    else:
        print("Only download is supported at the moment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
