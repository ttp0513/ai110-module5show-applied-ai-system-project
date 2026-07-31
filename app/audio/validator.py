"""Byte-level upload validation and bounded temporary storage."""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


class AudioValidationError(ValueError):
    """Raised when an upload violates an audio safety boundary."""


@dataclass(frozen=True)
class StoredUpload:
    path: Path
    detected_format: str
    size_bytes: int


SIGNATURES = {
    "wav": lambda data: data.startswith(b"RIFF") and data[8:12] == b"WAVE",
    "flac": lambda data: data.startswith(b"fLaC"),
    "ogg": lambda data: data.startswith(b"OggS"),
    "mp3": lambda data: (
        data.startswith(b"ID3")
        or (len(data) > 1 and data[0] == 0xFF and data[1] & 0xE0 == 0xE0)
    ),
    "m4a": lambda data: len(data) >= 12 and data[4:8] == b"ftyp",
}
ALLOWED_EXTENSIONS = {f".{name}" for name in SIGNATURES}


async def store_validated_upload(
    upload: UploadFile,
    upload_directory: Path,
    max_bytes: int,
) -> StoredUpload:
    """Stream a bounded upload to a randomized non-public path."""

    filename = Path(upload.filename or "").name
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise AudioValidationError("Use a WAV, FLAC, OGG, MP3, or M4A audio file.")

    header = await upload.read(32)
    detected = next(
        (name for name, matches in SIGNATURES.items() if matches(header)),
        None,
    )
    if detected is None or suffix != f".{detected}":
        raise AudioValidationError("The file contents do not match its audio format.")

    upload_directory.mkdir(parents=True, exist_ok=True)
    destination = upload_directory / f"{uuid4().hex}.{detected}"
    size = 0
    try:
        with destination.open("wb") as output:
            chunk = header
            while chunk:
                size += len(chunk)
                if size > max_bytes:
                    raise AudioValidationError(
                        "Audio must be no larger than "
                        f"{max_bytes // (1024 * 1024)} MiB."
                    )
                output.write(chunk)
                chunk = await upload.read(1024 * 1024)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    if size == 0:
        destination.unlink(missing_ok=True)
        raise AudioValidationError("The uploaded file is empty.")
    return StoredUpload(destination, detected, size)
