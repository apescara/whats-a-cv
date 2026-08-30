import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .atomic import atomic_write
from .diffs import unified_diff


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


class ProposalStore:
    def __init__(self, database: Path):
        self.database = database
        database.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(database) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY, target_path TEXT NOT NULL, old_hash TEXT NOT NULL,
                proposed_content TEXT NOT NULL, diff TEXT NOT NULL, status TEXT NOT NULL,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")

    def create(self, target_path: Path, proposed_content: str, relative_to: Path | None = None) -> int:
        old = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.database) as db:
            cursor = db.execute("INSERT INTO proposals(target_path,old_hash,proposed_content,diff,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                (str(target_path), content_hash(old), proposed_content, unified_diff(target_path, old, proposed_content, relative_to=relative_to), "pending", now, now))
            return cursor.lastrowid

    def get(self, proposal_id: int) -> sqlite3.Row | None:
        db = sqlite3.connect(self.database); db.row_factory = sqlite3.Row
        return db.execute("SELECT * FROM proposals WHERE id=?", (proposal_id,)).fetchone()

    def _finish(self, proposal_id: int, status: str) -> None:
        with sqlite3.connect(self.database) as db:
            db.execute("UPDATE proposals SET status=?,updated_at=? WHERE id=? AND status='pending'", (status, datetime.now(timezone.utc).isoformat(), proposal_id))

    def approve(self, proposal_id: int) -> None:
        row = self.get(proposal_id)
        if not row or row["status"] != "pending": raise ValueError("proposal is not pending")
        path = Path(row["target_path"]); current = path.read_text(encoding="utf-8") if path.exists() else ""
        if content_hash(current) != row["old_hash"]: raise ValueError("proposal is stale")
        atomic_write(path, row["proposed_content"]); self._finish(proposal_id, "approved")

    def reject(self, proposal_id: int) -> None:
        row = self.get(proposal_id)
        if not row or row["status"] != "pending": raise ValueError("proposal is not pending")
        self._finish(proposal_id, "rejected")
