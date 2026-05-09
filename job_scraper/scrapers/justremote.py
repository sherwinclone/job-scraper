import json
import re
import sys

import httpx

from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper

BASE_URL = "https://justremote.co"
# The SPA returns ALL jobs regardless of which category URL we hit, so one
# fetch is enough. The category field in the response is unreliable
# (e.g. "Senior Data Engineer" tagged as "manager") so we don't store it.
LANDING_PATH = "/remote-developer-jobs"
STATE_RE = re.compile(r"window\.__PRELOADED_STATE__\s*=\s*(.*?)</script>", re.S)


class JustRemoteScraper(BaseScraper):
    name = "justremote"

    def fetch(self) -> list[Job]:
        client = httpx.Client(
            headers={"User-Agent": "job-scraper/0.1"},
            timeout=30.0,
            follow_redirects=True,
        )
        try:
            resp = client.get(f"{BASE_URL}{LANDING_PATH}")
            resp.raise_for_status()
            jobs = self.parse(resp.text)
        except Exception as e:
            print(f"  [justremote] fetch failed: {e}", file=sys.stderr)
            jobs = []
        client.close()
        # Dedup by (title, company) — same job sometimes appears with multiple slugs.
        seen: set[tuple[str, str]] = set()
        unique: list[Job] = []
        for j in jobs:
            key = (j.title.strip().lower(), j.company.strip().lower())
            if key in seen:
                continue
            seen.add(key)
            unique.append(j)
        return unique

    def parse(self, html: str) -> list[Job]:
        m = STATE_RE.search(html)
        if not m:
            return []
        try:
            state = json.loads(m.group(1).strip().rstrip(";").strip())
        except Exception as e:
            print(f"  [justremote] state parse failed: {e}", file=sys.stderr)
            return []
        raw = state.get("jobsState", {}).get("entity", {}).get("all") or []
        jobs: list[Job] = []
        for entry in raw:
            href = entry.get("href", "")
            url = f"{BASE_URL}/{href.lstrip('/')}" if href else BASE_URL
            loc_list = entry.get("location_restrictions") or []
            location_bits = []
            if entry.get("remote_type"):
                location_bits.append(entry["remote_type"])
            if loc_list:
                location_bits.append(", ".join(loc_list))
            jobs.append(Job(
                id=f"justremote:{entry.get('id', href)}",
                platform=self.name,
                title=entry.get("title", ""),
                company=entry.get("company_name", ""),
                url=url,
                tags=[entry["job_type"]] if entry.get("job_type") else [],
                salary=None,
                location=" | ".join(location_bits) or None,
                posted_at=str(entry.get("date") or "") or None,
            ))
        return jobs
