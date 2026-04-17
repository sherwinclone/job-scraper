import sys
import time

import httpx

from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper

API_URL = "https://himalayas.app/jobs/api"
ASIA_TIMEZONES = {7, 8, 8.75, 9, 9.5, 10, 10.5, 11, 12}
MAX_SCAN = 5000  # scan up to 5000 jobs


class HimalayasScraper(BaseScraper):
    name = "himalayas"

    def fetch(self) -> list[Job]:
        client = httpx.Client(
            headers={"User-Agent": "job-scraper/0.1"},
            timeout=30.0,
        )
        all_jobs = []
        offset = 0
        limit = 20

        while offset < MAX_SCAN:
            try:
                resp = client.get(f"{API_URL}?limit={limit}&offset={offset}")
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"  [himalayas] Error at offset {offset}: {e}", file=sys.stderr)
                break

            raw_jobs = data.get("jobs", [])
            if not raw_jobs:
                break

            parsed = self.parse(raw_jobs)
            all_jobs.extend(parsed)

            if offset % 200 == 0:
                print(f"  [himalayas] scanned {offset + len(raw_jobs)} jobs, {len(all_jobs)} Asia-friendly so far", file=sys.stderr)

            offset += limit
            time.sleep(0.3)

        client.close()
        return all_jobs

    def parse(self, data: list[dict]) -> list[Job]:
        """Filter for Asia-timezone jobs only. Role filtering is done by filters.py."""
        jobs = []
        for entry in data:
            tz = entry.get("timezoneRestrictions", [])
            # Skip jobs that explicitly exclude Asia timezones
            if tz and not any(t in ASIA_TIMEZONES for t in tz):
                continue

            salary = self._format_salary(
                entry.get("minSalary", 0),
                entry.get("maxSalary", 0),
                entry.get("currency", "USD"),
            )
            loc_list = entry.get("locationRestrictions", [])
            location = " / ".join(loc_list) if loc_list else "Worldwide"

            jobs.append(Job(
                id=f"himalayas:{entry.get('guid', entry.get('title', ''))}",
                platform=self.name,
                title=entry["title"],
                company=entry.get("companyName", ""),
                url=entry.get("applicationLink", ""),
                tags=entry.get("categories", []),
                salary=salary,
                location=location,
                posted_at=str(entry.get("pubDate", "")),
            ))
        return jobs

    def _format_salary(self, min_val, max_val, currency: str) -> str | None:
        if not min_val and not max_val:
            return None
        if min_val and max_val:
            return f"${min_val:,.0f}-${max_val:,.0f} {currency}"
        if min_val:
            return f"${min_val:,.0f}+ {currency}"
        return f"Up to ${max_val:,.0f} {currency}"
