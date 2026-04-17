import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

from job_scraper.models import Job

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    url TEXT NOT NULL,
    tags TEXT,
    salary TEXT,
    location TEXT,
    posted_at TEXT,
    scraped_at TEXT NOT NULL,
    notified INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_jobs_platform ON jobs(platform);
CREATE INDEX IF NOT EXISTS idx_jobs_notified ON jobs(notified);
CREATE INDEX IF NOT EXISTS idx_jobs_posted ON jobs(posted_at);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped ON jobs(scraped_at);
"""


class Store:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        conn.executescript(_SCHEMA)
        conn.close()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, timeout=10)

    def job_exists(self, job_id: str) -> bool:
        conn = self._connect()
        row = conn.execute("SELECT 1 FROM jobs WHERE id = ?", (job_id,)).fetchone()
        conn.close()
        return row is not None

    def save_job(self, job: Job) -> bool:
        if self.job_exists(job.id):
            return False
        now = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        conn.execute(
            "INSERT INTO jobs (id, platform, title, company, url, tags, salary, location, posted_at, scraped_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (job.id, job.platform, job.title, job.company, job.url,
             ",".join(job.tags), job.salary, job.location, job.posted_at, now),
        )
        conn.commit()
        conn.close()
        return True

    def save_jobs(self, jobs: list[Job]) -> int:
        count = 0
        for job in jobs:
            if self.save_job(job):
                count += 1
        return count

    def get_unnotified_jobs(self) -> list[dict]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT id, platform, title, company, url, tags, salary, location, posted_at "
            "FROM jobs WHERE notified = 0 ORDER BY scraped_at DESC"
        ).fetchall()
        conn.close()
        return [
            {"id": r[0], "platform": r[1], "title": r[2], "company": r[3],
             "url": r[4], "tags": r[5], "salary": r[6], "location": r[7], "posted_at": r[8]}
            for r in rows
        ]

    def mark_notified(self, job_id: str):
        conn = self._connect()
        conn.execute("UPDATE jobs SET notified = 1 WHERE id = ?", (job_id,))
        conn.commit()
        conn.close()

    def get_recent_jobs(self, days: int = 7) -> list[dict]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        conn = self._connect()
        rows = conn.execute(
            "SELECT id, platform, title, company, url, tags, salary, location, posted_at "
            "FROM jobs WHERE scraped_at >= ? ORDER BY scraped_at DESC",
            (cutoff,),
        ).fetchall()
        conn.close()
        return [
            {"id": r[0], "platform": r[1], "title": r[2], "company": r[3],
             "url": r[4], "tags": r[5], "salary": r[6], "location": r[7], "posted_at": r[8]}
            for r in rows
        ]

    def get_stats(self) -> dict:
        conn = self._connect()
        total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        by_platform = conn.execute(
            "SELECT platform, COUNT(*) FROM jobs GROUP BY platform ORDER BY COUNT(*) DESC"
        ).fetchall()
        conn.close()
        return {
            "total_jobs": total,
            "by_platform": {r[0]: r[1] for r in by_platform},
        }
