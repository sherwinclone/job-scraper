from job_scraper.models import Job
from job_scraper.store import Store


def _job(id="test:1", title="Data Engineer", company="TestCo"):
    return Job(
        id=id, platform="test", title=title, company=company,
        url="https://example.com", tags=["python", "spark"],
        salary="$120K", location="Worldwide", posted_at="2026-04-17",
    )


class TestStore:
    def test_init_creates_table(self, tmp_path):
        store = Store(tmp_path / "test.db")
        import sqlite3
        conn = sqlite3.connect(tmp_path / "test.db")
        tables = {t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert "jobs" in tables
        conn.close()

    def test_save_and_exists(self, tmp_path):
        store = Store(tmp_path / "test.db")
        job = _job()
        assert not store.job_exists("test:1")
        store.save_job(job)
        assert store.job_exists("test:1")

    def test_skip_duplicate(self, tmp_path):
        store = Store(tmp_path / "test.db")
        store.save_job(_job())
        store.save_job(_job())
        assert store.get_stats()["total_jobs"] == 1

    def test_save_batch(self, tmp_path):
        store = Store(tmp_path / "test.db")
        jobs = [_job("t:1"), _job("t:2"), _job("t:3")]
        new_count = store.save_jobs(jobs)
        assert new_count == 3
        assert store.get_stats()["total_jobs"] == 3

    def test_save_batch_skips_existing(self, tmp_path):
        store = Store(tmp_path / "test.db")
        store.save_job(_job("t:1"))
        new_count = store.save_jobs([_job("t:1"), _job("t:2")])
        assert new_count == 1

    def test_get_unnotified(self, tmp_path):
        store = Store(tmp_path / "test.db")
        store.save_jobs([_job("t:1"), _job("t:2")])
        unnotified = store.get_unnotified_jobs()
        assert len(unnotified) == 2

    def test_mark_notified(self, tmp_path):
        store = Store(tmp_path / "test.db")
        store.save_job(_job("t:1"))
        store.mark_notified("t:1")
        assert len(store.get_unnotified_jobs()) == 0

    def test_get_recent(self, tmp_path):
        store = Store(tmp_path / "test.db")
        store.save_jobs([_job("t:1"), _job("t:2")])
        recent = store.get_recent_jobs(days=7)
        assert len(recent) == 2
