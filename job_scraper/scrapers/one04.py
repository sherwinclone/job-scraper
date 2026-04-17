"""104 人力銀行 scraper — uses their internal JSON API."""
import httpx

from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper

API_URL = "https://www.104.com.tw/jobs/search/api/jobs"
SEARCH_QUERIES = [
    "data engineer",
    "backend engineer remote",
    "Spark Python",
    "SRE engineer",
    "DevOps engineer remote",
    "Python 後端",
    "資料工程師",
]


class One04Scraper(BaseScraper):
    name = "104"

    def fetch(self) -> list[Job]:
        client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://www.104.com.tw/",
                "Accept": "application/json",
            },
            timeout=30.0,
        )
        seen_ids = set()
        all_jobs = []

        for query in SEARCH_QUERIES:
            try:
                resp = client.get(API_URL, params={
                    "keyword": query,
                    "page": 1,
                    "pageSize": 50,
                    "remoteWork": 1,  # remote jobs only
                })
                if resp.status_code != 200:
                    continue
                data = resp.json()
                for j in self._parse_entries(data.get("data", [])):
                    if j.id not in seen_ids:
                        seen_ids.add(j.id)
                        all_jobs.append(j)
            except Exception:
                continue

        client.close()
        return all_jobs

    def parse(self, data: list[dict]) -> list[Job]:
        return self._parse_entries(data)

    def _parse_entries(self, entries: list) -> list[Job]:
        jobs = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            remote_type = entry.get("remoteWorkType", 0)
            if remote_type == 0:
                continue  # not remote

            job_no = entry.get("jobNo", "")
            link = entry.get("link", {})
            job_url = link.get("job", f"https://www.104.com.tw/job/{job_no}") if isinstance(link, dict) else f"https://www.104.com.tw/job/{job_no}"

            salary_low = entry.get("salaryLow", 0)
            salary_high = entry.get("salaryHigh", 0)
            salary_desc = entry.get("salaryDesc", "")
            salary = salary_desc if salary_desc and salary_desc != "面議" else None

            jobs.append(Job(
                id=f"104:{job_no}",
                platform=self.name,
                title=entry.get("jobName", ""),
                company=entry.get("custName", ""),
                url=job_url,
                tags=[],
                salary=salary,
                location=entry.get("jobAddrNoDesc", ""),
                posted_at=entry.get("appearDate", ""),
            ))
        return jobs
