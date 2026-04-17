import httpx
from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper


class RemotiveScraper(BaseScraper):
    name = "remotive"
    API_URL = "https://remotive.com/api/remote-jobs?category=software-dev"

    def fetch(self) -> list[Job]:
        resp = httpx.get(self.API_URL, headers={"User-Agent": "job-scraper/0.1"}, timeout=30.0)
        resp.raise_for_status()
        return self.parse(resp.json())

    def parse(self, data: dict) -> list[Job]:
        jobs = []
        for entry in data.get("jobs", []):
            salary = entry.get("salary", "").strip() or None
            jobs.append(Job(
                id=f"remotive:{entry['id']}",
                platform=self.name,
                title=entry["title"],
                company=entry.get("company_name", ""),
                url=entry.get("url", ""),
                tags=entry.get("tags", []),
                salary=salary,
                location=entry.get("candidate_required_location", ""),
                posted_at=entry.get("publication_date", ""),
            ))
        return jobs
