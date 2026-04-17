"""Scraper using python-jobspy library to search LinkedIn, Indeed, Glassdoor, Google Jobs."""
import sys

from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper

SEARCH_QUERIES = [
    "data engineer",
    "analytics engineer",
    "data platform engineer",
    "Databricks engineer",
]

# Search in countries with Asia-friendly remote jobs
SEARCH_LOCATIONS = [
    "Singapore",
    "Australia",
    "Taiwan",
    "Japan",
]


class JobSpyScraper(BaseScraper):
    name = "jobspy"

    def fetch(self) -> list[Job]:
        try:
            from jobspy import scrape_jobs
        except ImportError:
            print("[jobspy] python-jobspy not installed, skipping", file=sys.stderr)
            return []

        seen_ids = set()
        all_jobs = []

        for query in SEARCH_QUERIES:
            for location in SEARCH_LOCATIONS:
                try:
                    results = scrape_jobs(
                        site_name=["linkedin", "indeed", "glassdoor"],
                        search_term=query,
                        location=location,
                        results_wanted=20,
                        is_remote=True,
                        country_indeed="singapore",
                    )
                    for _, row in results.iterrows():
                        job = self._row_to_job(row)
                        if job and job.id not in seen_ids:
                            seen_ids.add(job.id)
                            all_jobs.append(job)
                except Exception as e:
                    print(f"[jobspy] Error searching '{query}' in {location}: {e}", file=sys.stderr)
                    continue

        return all_jobs

    def parse(self, data) -> list[Job]:
        """Not used directly — fetch() handles everything via jobspy library."""
        return []

    def _row_to_job(self, row) -> Job | None:
        title = str(row.get("title", ""))
        company = str(row.get("company_name", ""))
        if not title or not company:
            return None

        job_url = str(row.get("job_url", ""))
        site = str(row.get("site", ""))
        job_id = str(row.get("id", "")) or job_url

        salary_min = row.get("min_amount")
        salary_max = row.get("max_amount")
        salary_currency = str(row.get("currency", "USD"))
        salary = None
        if salary_min and salary_max:
            salary = f"${salary_min:,.0f}-${salary_max:,.0f} {salary_currency}"
        elif salary_min:
            salary = f"${salary_min:,.0f}+ {salary_currency}"

        location = str(row.get("location", ""))
        date_posted = str(row.get("date_posted", ""))

        return Job(
            id=f"jobspy:{site}:{job_id}",
            platform=f"jobspy-{site}",
            title=title,
            company=company,
            url=job_url,
            tags=[],
            salary=salary,
            location=location,
            posted_at=date_posted,
        )
