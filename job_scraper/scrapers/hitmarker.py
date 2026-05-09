import sys

import httpx
from bs4 import BeautifulSoup

from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper

BASE_URL = "https://hitmarker.net"
LISTING_URL = f"{BASE_URL}/jobs"


class HitmarkerScraper(BaseScraper):
    """Gaming/esports jobs.

    Hitmarker's listing is fully client-rendered: only ~12 cards are present in
    the SSR HTML, query-string filters (?industry=data) are ignored on the
    server, and pagination is JS-driven. We collect what's in the SSR page and
    let filters.py downstream pick out data/engineering roles.
    """

    name = "hitmarker"

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
            print(f"  [hitmarker] fetch failed: {e}", file=sys.stderr)
            return []
        return self.parse(resp.text)

    def parse(self, html: str) -> list[Job]:
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[Job] = []
        for a in soup.select('a[href*="/jobs/"]'):
            href = a.get("href", "")
            # Detail-page links live at /jobs/<slug>-<numeric-id>
            if not href or "/jobs/" not in href:
                continue
            slug = href.rstrip("/").split("/jobs/")[-1]
            if not slug or "/" in slug or slug == "new":
                continue
            title_el = a.select_one("div.font-bold")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                continue
            # Company + location sit in the two flex rows below the title.
            company = ""
            location = None
            text_spans = a.select("span.text-alpha-7")
            if text_spans:
                company = text_spans[0].get_text(strip=True)
                if len(text_spans) > 1:
                    location = text_spans[1].get_text(" ", strip=True) or None
            url = href if href.startswith("http") else f"{BASE_URL}{href}"
            jobs.append(Job(
                id=f"hitmarker:{slug}",
                platform=self.name,
                title=title,
                company=company,
                url=url,
                tags=["gaming", "esports"],
                salary=None,
                location=location,
                posted_at=None,
            ))
        return jobs
