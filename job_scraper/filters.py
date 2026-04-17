import re

from job_scraper.models import Job

ROLE_KEYWORDS = [
    "data engineer", "analytics engineer", "data platform",
    "data scientist", "data analyst", "data infrastructure",
    "data ops", "dataops", "databricks", "spark",
    "etl", "airflow", "data pipeline", "data warehouse",
    "資料工程", "數據工程", "資料分析",
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


def matches_timezone(job: Job) -> bool:
    loc = (job.location or "").lower().strip()
    if not loc:
        return True
    if any(ex in loc for ex in TIMEZONE_EXCLUDE):
        return False
    if any(inc in loc for inc in TIMEZONE_INCLUDE):
        return True
    return True


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
        if matches_role(j) and matches_timezone(j) and matches_seniority(j) and matches_salary(j)
    ]
