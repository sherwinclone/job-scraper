from job_scraper.models import Job

ROLE_KEYWORDS = [
    "data engineer", "analytics engineer", "data platform",
    "backend engineer", "backend developer", "python developer",
    "platform engineer", "site reliability", "sre",
    "etl", "databricks", "spark", "airflow",
    "data infrastructure", "data ops", "python",
]

TIMEZONE_INCLUDE = [
    "worldwide", "anywhere", "global",
    "asia", "apac", "utc+7", "utc+8", "utc+9",
    "singapore", "japan", "australia", "taiwan", "hong kong", "korea",
    "indonesia", "malaysia", "india", "vietnam", "thailand", "philippines",
]

TIMEZONE_EXCLUDE = [
    "us only", "usa only", "americas only",
    "eu only", "europe only", "uk only",
]


def matches_role(job: Job) -> bool:
    text = (job.title + " " + " ".join(job.tags)).lower()
    return any(kw in text for kw in ROLE_KEYWORDS)


def matches_timezone(job: Job) -> bool:
    loc = (job.location or "").lower().strip()
    if not loc:
        return True
    if any(ex in loc for ex in TIMEZONE_EXCLUDE):
        return False
    if any(inc in loc for inc in TIMEZONE_INCLUDE):
        return True
    return True


def filter_jobs(jobs: list[Job]) -> list[Job]:
    return [j for j in jobs if matches_role(j) and matches_timezone(j)]
