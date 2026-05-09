import json
import re
import sys

import httpx

from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper

BASE_URL = "https://justremote.co"
# The advertised "/feed" URL actually returns the React SPA; the real RSS no
# longer exists. The category landing pages, however, ship the full job list
# in window.__PRELOADED_STATE__, which we extract here.
CATEGORY_PATHS = [
    "/remote-developer-jobs",
    "/remote-devops-sysadmin-jobs",
]
STATE_RE = re.compile(r"window\.__PRELOADED_STATE__\s*=\s*(.*?)</script>", re.S)


class JustRemoteScraper(BaseScraper):
    name = "justremote"

    def fetch(self) -> list[Job]:
        client = httpx.Client(
            headers={"User-Agent": "job-scraper/0.1"},
            timeout=30.0,
            follow_redirects=True,
        )
        all_jobs: list[Job] = []
        seen: set[str] = set()
        for path in CATEGORY_PATHS:
            try:
                resp = client.get(f"{BASE_URL}{path}")
                resp.raise_for_status()
            except Exception as e:
                print(f"  [justremote] fetch {path} failed: {e}", file=sys.stderr)
                continue
            for job in self.parse(resp.text):
                if job.id in seen:
                    continue
                seen.add(job.id)
                all_jobs.append(job)
        client.close()
        return all_jobs

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
                tags=[t for t in [entry.get("category"), entry.get("job_type")] if t],
                salary=None,
                location=" | ".join(location_bits) or None,
                posted_at=str(entry.get("date") or "") or None,
            ))
        return jobs
