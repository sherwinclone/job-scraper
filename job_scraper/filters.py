import re

from job_scraper.models import Job

ROLE_KEYWORDS = [
    "data engineer", "analytics engineer", "data platform",
    "data scientist", "data analyst", "data infrastructure",
    "data ops", "dataops", "databricks", "spark",
    "etl", "airflow", "data pipeline", "data warehouse",
    "資料工程", "數據工程", "資料分析",
]

# Locations that mean "fully remote, worldwide".
REMOTE_INCLUDE = [
    "worldwide", "anywhere", "global",
    "fully remote", "100% remote", "remote-first", "fully-remote",
    "remote · global", "remote / global",
]

# Taiwan-only is OK (Sherwin is in Taiwan); other country-only locks rejected.
TAIWAN_ONLY = ["taiwan", "台灣", "台北", "taipei"]

# Locations that disqualify the job: country/region locks, on-site, hybrid.
LOCATION_EXCLUDE = [
    "us only", "usa only", "united states only", "u.s. only",
    "americas only", "north america only", "latam only", "south america only",
    "eu only", "europe only", "european union only", "eea only",
    "uk only", "united kingdom only", "ireland only",
    "asia only", "apac only",
    "canada only", "australia only", "anz only", "new zealand only",
    "singapore only", "japan only", "hong kong only", "korea only",
    "india only", "vietnam only", "thailand only", "philippines only",
    # On-site / hybrid indicators
    "on-site", "onsite", "on site",
    "hybrid",
    "in-office", "in office", "in-person", "in person",
]

# Exclude junior/intern/low-level/unrelated titles
TITLE_EXCLUDE = [
    "junior", "intern", "實習", "講師", "助理", "assistant",
    "manager", "director", "vp ", "vice president", "head of",
    "主管", "經理", "總監",
    "unpaid", "volunteer", "志工",
    "accelerator program",
    "designer", "設計師",
    "react developer", "frontend", "前端",
    "接案", "約聘", "兼職", "part-time", "freelance",
    "online data analyst",  # usually crowd-sourcing gigs
]

# Min salary: $150K USD for international, 150萬 TWD for 104
MIN_SALARY_USD = 150000
MIN_SALARY_TWD = 1500000


def matches_role(job: Job) -> bool:
    text = (job.title + " " + " ".join(job.tags)).lower()
    return any(kw in text for kw in ROLE_KEYWORDS)


def matches_remote(job: Job) -> bool:
    """Accept fully-remote (worldwide) jobs and Taiwan-only jobs.

    Rejects region-locked listings (US-only, EU-only, etc. except Taiwan),
    hybrid, and on-site listings.
    """
    loc = (job.location or "").lower().strip()
    if not loc:
        # No location info — let other filters decide.
        return True
    # Hard rejects: any explicit lock or non-remote signal.
    if any(ex in loc for ex in LOCATION_EXCLUDE):
        return False
    # Taiwan-only is allowed (Sherwin is local).
    if any(tw in loc for tw in TAIWAN_ONLY):
        return True
    # Worldwide / global remote keywords accepted.
    if any(inc in loc for inc in REMOTE_INCLUDE):
        return True
    # Plain "remote" (most boards tag this for fully-remote).
    if "remote" in loc:
        return True
    # Specific city/country with no remote keyword → not fully remote.
    return False


def matches_seniority(job: Job) -> bool:
    """Exclude junior/intern and management titles."""
    title_lower = job.title.lower()
    return not any(ex in title_lower for ex in TITLE_EXCLUDE)


def _parse_twd_from_title(title: str) -> int | None:
    """Extract TWD salary from 104 titles like '月薪 5-9 萬' or '年薪 100-170 萬'."""
    # 年薪 pattern
    m = re.search(r"年薪\s*(\d+)\s*[-~]\s*(\d+)\s*萬", title)
    if m:
        return int(m.group(2)) * 10000  # use max
    # 月薪 pattern → convert to annual
    m = re.search(r"月薪\s*(\d+)\s*[-~]\s*(\d+)\s*萬", title)
    if m:
        return int(m.group(2)) * 10000 * 12  # max monthly × 12
    return None


def matches_salary(job: Job) -> bool:
    """Exclude jobs with salary explicitly below threshold."""
    if job.platform == "104":
        # Try to parse salary from title (104 often puts it there)
        twd = _parse_twd_from_title(job.title)
        if twd is not None:
            return twd >= MIN_SALARY_TWD
        return True  # 面議 = can't filter, keep it
    if not job.salary:
        return True  # no salary info = don't exclude
    # Try to extract max salary number from string like "$80k", "$80,000", "$80K - $120K"
    numbers = re.findall(r"\$?([\d,]+)\s*k", job.salary, re.IGNORECASE)
    if numbers:
        max_val = max(int(n.replace(",", "")) * 1000 for n in numbers)
        return max_val >= MIN_SALARY_USD
    numbers = re.findall(r"\$?([\d,]+)", job.salary)
    if numbers:
        max_val = max(int(n.replace(",", "")) for n in numbers)
        if max_val > 1000:  # looks like actual salary, not hourly
            return max_val >= MIN_SALARY_USD
    return True  # can't parse = don't exclude


def filter_jobs(jobs: list[Job]) -> list[Job]:
    return [
        j for j in jobs
        if matches_role(j) and matches_remote(j) and matches_seniority(j) and matches_salary(j)
    ]
