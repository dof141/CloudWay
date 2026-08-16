"""SQLite cache for processed Xiaohongshu attraction summaries."""

import hashlib
import os
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional


DEFAULT_FRESH_TTL_SECONDS = 60 * 60
DEFAULT_MAX_TTL_SECONDS = 24 * 60 * 60


@dataclass(frozen=True)
class XhsCacheEntry:
    result_text: str
    age_seconds: int
    is_fresh: bool


class XhsAttractionCache:
    """Persist final attraction summaries without storing cookies or raw notes."""

    def __init__(self, db_path: Optional[str] = None):
        backend_dir = Path(__file__).resolve().parents[2]
        configured_path = db_path or os.getenv("XHS_CACHE_DB_PATH", "")
        self.db_path = (
            Path(configured_path).expanduser().resolve()
            if configured_path
            else backend_dir / "data" / "xhs_cache.db"
        )
        self.fresh_ttl = max(
            0,
            int(os.getenv("XHS_CACHE_FRESH_TTL_SECONDS", str(DEFAULT_FRESH_TTL_SECONDS))),
        )
        self.max_ttl = max(
            self.fresh_ttl,
            int(os.getenv("XHS_CACHE_TTL_SECONDS", str(DEFAULT_MAX_TTL_SECONDS))),
        )
        self.enabled = os.getenv("XHS_CACHE_ENABLED", "true").lower() == "true"

    @staticmethod
    def _cache_key(city: str, keywords: str, language: str) -> str:
        normalized = "\n".join(
            part.strip().lower() for part in (city, keywords, language or "zh")
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path, timeout=5)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=5000")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS xhs_attraction_cache (
                cache_key TEXT PRIMARY KEY,
                city TEXT NOT NULL,
                keyword TEXT NOT NULL,
                language TEXT NOT NULL,
                result_text TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            )
            """
        )
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def get(self, city: str, keywords: str, language: str) -> Optional[XhsCacheEntry]:
        if not self.enabled:
            return None

        cache_key = self._cache_key(city, keywords, language)
        try:
            with self._connection() as connection:
                row = connection.execute(
                    "SELECT result_text, updated_at FROM xhs_attraction_cache WHERE cache_key = ?",
                    (cache_key,),
                ).fetchone()
            if not row:
                return None

            age_seconds = max(0, int(time.time()) - int(row[1]))
            if age_seconds > self.max_ttl:
                self.delete(cache_key)
                return None
            return XhsCacheEntry(
                result_text=str(row[0]),
                age_seconds=age_seconds,
                is_fresh=age_seconds <= self.fresh_ttl,
            )
        except (OSError, sqlite3.Error, ValueError):
            return None

    def put(self, city: str, keywords: str, language: str, result_text: str) -> None:
        if not self.enabled or not result_text.strip():
            return

        cache_key = self._cache_key(city, keywords, language)
        now = int(time.time())
        try:
            with self._connection() as connection:
                connection.execute(
                    """
                    INSERT INTO xhs_attraction_cache (
                        cache_key, city, keyword, language, result_text, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(cache_key) DO UPDATE SET
                        result_text = excluded.result_text,
                        updated_at = excluded.updated_at
                    """,
                    (cache_key, city, keywords, language, result_text, now),
                )
                connection.execute(
                    "DELETE FROM xhs_attraction_cache WHERE updated_at < ?",
                    (now - self.max_ttl,),
                )
        except (OSError, sqlite3.Error):
            return

    def delete(self, cache_key: str) -> None:
        try:
            with self._connection() as connection:
                connection.execute(
                    "DELETE FROM xhs_attraction_cache WHERE cache_key = ?",
                    (cache_key,),
                )
        except (OSError, sqlite3.Error):
            return


xhs_attraction_cache = XhsAttractionCache()
