import httpx
from bs4 import BeautifulSoup
from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper

BASE_URL = "https://weworkremotely.com"
CATEGORIES = [
    "/categories/remote-back-end-programming-jobs",
    "/categories/remote-devops-sysadmin-jobs",
]


class WeWorkRemotelyScraper(BaseScraper):
    name = "weworkremotely"

    def fetch(self) -> list[Job]:
        all_jobs = []
        for category in CATEGORIES:
            resp = httpx.get(f"{BASE_URL}{category}", headers={"User-Agent": "job-scraper/0.1"}, timeout=30.0)
            resp.raise_for_status()
            all_jobs.extend(self.parse(resp.text))
        return all_jobs

    def parse(self, html: str) -> list[Job]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        for li in soup.select("li.new-listing-container"):
            link = li.select_one("a.listing-link--unlocked")
            if not link:
                continue
            href = link.get("href", "")
            title_el = link.select_one("span.new-listing__header__title__text")
            company_el = link.select_one("p.new-listing__company-name")
            categories = [p.get_text(strip=True) for p in link.select("p.new-listing__categories__category")]
            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            location = " ".join(categories)
            slug = href.split("/")[-1] if href else ""
            jobs.append(Job(
                id=f"weworkremotely:{slug}",
                platform=self.name,
                title=title,
                company=company,
                url=f"{BASE_URL}{href}",
                tags=[],
                salary=None,
                location=location,
                posted_at=None,
            ))
        return jobs
