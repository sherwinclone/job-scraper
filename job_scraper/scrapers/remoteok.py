import httpx
from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper


class RemoteOKScraper(BaseScraper):
    name = "remoteok"
    API_URL = "https://remoteok.com/api"

    def fetch(self) -> list[Job]:
        resp = httpx.get(self.API_URL, headers={"User-Agent": "job-scraper/0.1"}, timeout=30.0)
        resp.raise_for_status()
        return self.parse(resp.json())

    def parse(self, data: list[dict]) -> list[Job]:
        jobs = []
        for entry in data:
            if "id" not in entry or "position" not in entry:
                continue
            salary = self._format_salary(entry.get("salary_min", 0), entry.get("salary_max", 0))
            jobs.append(Job(
                id=f"remoteok:{entry['id']}",
                platform=self.name,
                title=entry["position"],
                company=entry.get("company", ""),
                url=entry.get("url", ""),
                tags=entry.get("tags", []),
                salary=salary,
                location=entry.get("location", ""),
                posted_at=entry.get("date", ""),
            ))
        return jobs

    def _format_salary(self, min_val: int, max_val: int) -> str | None:
        if not min_val and not max_val:
            return None
        if min_val and max_val:
            return f"${min_val:,} - ${max_val:,}"
        if min_val:
            return f"${min_val:,}+"
        return f"Up to ${max_val:,}"
