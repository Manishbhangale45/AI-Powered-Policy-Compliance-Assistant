from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3
from pathlib import Path
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    original_name TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    checksum TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    chunk_count INTEGER NOT NULL,
    status TEXT NOT NULL,
    uploaded_at TEXT NOT NULL
);
"""


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    document_id: str
    original_name: str
    stored_path: str
    checksum: str
    mime_type: str
    chunk_count: int
    status: str
    uploaded_at: str


class SQLiteRegistry:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA)
            connection.commit()

    def upsert_document(self, record: DocumentRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id, original_name, stored_path, checksum,
                    mime_type, chunk_count, status, uploaded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    original_name=excluded.original_name,
                    stored_path=excluded.stored_path,
                    checksum=excluded.checksum,
                    mime_type=excluded.mime_type,
                    chunk_count=excluded.chunk_count,
                    status=excluded.status,
                    uploaded_at=excluded.uploaded_at
                """,
                (
                    record.document_id,
                    record.original_name,
                    record.stored_path,
                    record.checksum,
                    record.mime_type,
                    record.chunk_count,
                    record.status,
                    record.uploaded_at,
                ),
            )
            connection.commit()

    def list_documents(self) -> list[DocumentRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT document_id, original_name, stored_path, checksum, mime_type, chunk_count, status, uploaded_at FROM documents ORDER BY uploaded_at DESC"
            ).fetchall()
        return [DocumentRecord(**dict(row)) for row in rows]

    def get_document(self, document_id: str) -> DocumentRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT document_id, original_name, stored_path, checksum, mime_type, chunk_count, status, uploaded_at FROM documents WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        return DocumentRecord(**dict(row)) if row else None

    def delete_document(self, document_id: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
            connection.commit()

    @staticmethod
    def now_utc() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def from_record(cls, record: DocumentRecord) -> DocumentRecord:
        return record

    @staticmethod
    def build_record(
        document_id: str,
        original_name: str,
        stored_path: str,
        checksum: str,
        mime_type: str,
        chunk_count: int,
        status: str = "indexed",
    ) -> DocumentRecord:
        return DocumentRecord(
            document_id=document_id,
            original_name=original_name,
            stored_path=stored_path,
            checksum=checksum,
            mime_type=mime_type,
            chunk_count=chunk_count,
            status=status,
            uploaded_at=SQLiteRegistry.now_utc(),
        )

    def upsert_many(self, records: Iterable[DocumentRecord]) -> None:
        for record in records:
            self.upsert_document(record)
