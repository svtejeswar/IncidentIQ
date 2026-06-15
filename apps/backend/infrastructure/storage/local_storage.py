from __future__ import annotations

import os
import uuid
from pathlib import Path

import aiofiles

from application.interfaces.file_storage import IFileStorage
from core.logging.logger import get_logger

log = get_logger(__name__)


class LocalFileStorage(IFileStorage):
    def __init__(self, upload_dir: str) -> None:
        self._base_dir = Path(upload_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file_data: bytes, filename: str) -> str:
        safe_name = f"{uuid.uuid4()}_{self._sanitize(filename)}"
        file_path = self._base_dir / safe_name
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_data)
        log.info("file_saved", path=str(file_path), size=len(file_data))
        return str(file_path)

    async def read(self, file_path: str) -> bytes:
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    async def delete(self, file_path: str) -> bool:
        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        except OSError:
            return False

    async def exists(self, file_path: str) -> bool:
        return Path(file_path).exists()

    def _sanitize(self, filename: str) -> str:
        return "".join(c for c in filename if c.isalnum() or c in "._- ").strip()
