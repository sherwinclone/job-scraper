import sys

import httpx

from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper

# The advertised RSS endpoint (/jobsrss) now 404s. Working Nomads instead
# exposes a public JSON feed at /api/exposed_jobs/ which serves all currently
# visible jobs across categories. We use that and tag everything by the
# category_name field so filters.py can pick the data/dev/devops slice.
API_URL = "https://www.workingnomads.com/api/exposed_jobs/"


class WorkingNomadsScraper(BaseScraper):
    name = "workingnomads"

    def fetch(self) -> list[Job]:
        try:
            resp = httpx.get(
                API_URL,
                headers={"User-Agent": "job-scraper/0.1"},
                timeout=30.0,
                follow_redirects=True,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [workingnomads] fetch failed: {e}", file=sys.stderr)
            return []
        return self.parse(data)

    def parse(self, data: list[dict]) -> list[Job]:
        jobs: list[Job] = []
        for entry in data or []:
            url = entry.get("url", "")
            # Job IDs are embedded in the URL: .../job/go/<id>/
            jid = url.rstrip("/").split("/")[-1] if url else entry.get("title", "")
            tags_str = entry.get("tags", "") or ""
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            category = entry.get("category_name")
            if category and category.lower() not in (t.lower() for t in tags):
                tags.insert(0, category)
            jobs.append(Job(
                id=f"workingnomads:{jid}",
                platform=self.name,
                title=entry.get("title", ""),
                company=entry.get("company_name", ""),
                url=url,
                tags=tags,
                salary=None,
                location=entry.get("location") or None,
                posted_at=entry.get("pub_date") or None,
            ))
        return jobs
