import re
import sys

import httpx
from bs4 import BeautifulSoup

from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper

BASE_URL = "https://www.parlayjobs.com"
LISTING_URL = f"{BASE_URL}/jobs"
DETAIL_RE = re.compile(r"^/jobs/[a-z0-9-]+-[0-9a-f]{8}$")


class ParlayJobsScraper(BaseScraper):
    """Sports betting / iGaming jobs (Jobboardly-powered board).

    The /jobs page returns ~50 cards in SSR HTML. Query-string filters
    (?category=Data) 404, so we collect all cards and tag them with the
    industry; filters.py picks out data/backend/devops downstream.
    """

    name = "parlayjobs"

    def fetch(self) -> list[Job]:
        try:
            resp = httpx.get(
                LISTING_URL,
                headers={"User-Agent": "job-scraper/0.1"},
                timeout=30.0,
                follow_redirects=True,
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"  [parlayjobs] fetch failed: {e}", file=sys.stderr)
            return []
        return self.parse(resp.text)

    def parse(self, html: str) -> list[Job]:
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[Job] = []
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if not DETAIL_RE.match(href):
                continue
            slug = href.split("/jobs/")[-1]
            title_el = a.select_one("h3")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            company_el = title_el.find_next("p")
            company = company_el.get_text(strip=True) if company_el else ""
            # Pull whatever extra small <p> text the card carries (job type,
            # location). Skip the company paragraph we already captured.
            extras = [
                p.get_text(" ", strip=True)
                for p in a.select("p")
                if p is not company_el and p.get_text(strip=True)
            ]
            location = " | ".join(extras) if extras else None
            jobs.append(Job(
                id=f"parlayjobs:{slug}",
                platform=self.name,
                title=title,
                company=company,
                url=f"{BASE_URL}{href}",
                tags=["igaming", "sports-betting"],
                salary=None,
                location=location,
                posted_at=None,
            ))
        return jobs
