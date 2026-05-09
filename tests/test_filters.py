from job_scraper.models import Job
from job_scraper.filters import matches_role, matches_remote, filter_jobs


def _job(title="Data Engineer", tags=None, location=None):
    return Job(
        id="test:1", platform="test", title=title, company="TestCo",
        url="https://example.com", tags=tags or [], salary=None,
        location=location, posted_at=None,
    )


class TestMatchesRole:
    def test_data_engineer_title(self):
        assert matches_role(_job("Senior Data Engineer"))

    def test_data_platform_title(self):
        assert matches_role(_job("Data Platform Engineer"))

    def test_irrelevant_title(self):
        assert not matches_role(_job("Marketing Manager"))

    def test_matches_via_tags(self):
        assert matches_role(_job("Software Engineer", tags=["python", "spark"]))

    def test_case_insensitive(self):
        assert matches_role(_job("ANALYTICS ENGINEER"))

    def test_databricks_tag(self):
        assert matches_role(_job("Engineer", tags=["databricks"]))


class TestMatchesRemote:
    # Accepted: worldwide / global remote
    def test_worldwide(self):
        assert matches_remote(_job(location="Worldwide"))

    def test_anywhere(self):
        assert matches_remote(_job(location="Anywhere in the World"))

    def test_global(self):
        assert matches_remote(_job(location="Global"))

    def test_fully_remote(self):
        assert matches_remote(_job(location="Fully Remote"))

    def test_plain_remote(self):
        assert matches_remote(_job(location="Remote"))

    # Empty / unknown — let other filters decide
    def test_empty_location(self):
        assert matches_remote(_job(location=None))

    def test_empty_string_location(self):
        assert matches_remote(_job(location=""))

    # Taiwan-only is allowed exception (Sherwin is local)
    def test_taiwan_only_allowed(self):
        assert matches_remote(_job(location="Taiwan only"))

    def test_taipei_allowed(self):
        assert matches_remote(_job(location="Taipei, Taiwan"))

    def test_taiwan_chinese(self):
        assert matches_remote(_job(location="台北"))

    # Region-locked listings rejected
    def test_us_only_rejected(self):
        assert not matches_remote(_job(location="US Only"))

    def test_usa_only_rejected(self):
        assert not matches_remote(_job(location="USA only"))

    def test_europe_only_rejected(self):
        assert not matches_remote(_job(location="Europe Only"))

    def test_uk_only_rejected(self):
        assert not matches_remote(_job(location="UK only"))

    def test_americas_only_rejected(self):
        assert not matches_remote(_job(location="Americas only"))

    def test_singapore_only_rejected(self):
        assert not matches_remote(_job(location="Singapore only"))

    def test_japan_only_rejected(self):
        assert not matches_remote(_job(location="Japan only"))

    # Specific city/country with no remote keyword → not fully remote
    def test_specific_city_rejected(self):
        assert not matches_remote(_job(location="Berlin, Germany"))

    def test_specific_country_rejected(self):
        assert not matches_remote(_job(location="Singapore"))

    # Hybrid / on-site rejected
    def test_hybrid_rejected(self):
        assert not matches_remote(_job(location="Hybrid - London"))

    def test_onsite_rejected(self):
        assert not matches_remote(_job(location="On-site, NYC"))

    def test_in_office_rejected(self):
        assert not matches_remote(_job(location="In office, Berlin"))

    # Country-locked remote patterns rejected
    def test_japan_dash_remote_rejected(self):
        assert not matches_remote(_job(location="Japan - Remote"))

    def test_germany_dash_remote_rejected(self):
        assert not matches_remote(_job(location="Germany-Remote"))

    def test_remote_europe_parens_rejected(self):
        assert not matches_remote(_job(location="Remote (Europe)"))

    def test_remote_asia_parens_rejected(self):
        assert not matches_remote(_job(location="Remote (Asia)"))

    def test_remote_in_germany_rejected(self):
        assert not matches_remote(_job(location="Remote in Germany"))

    def test_remote_from_japan_rejected(self):
        assert not matches_remote(_job(location="Remote from Japan"))

    # Remote-friendly with city/state/country in parens (commas inside) → still accepted
    def test_remote_friendly_with_full_address_accepted(self):
        # bet365-style listing — Sherwin found this useful
        assert matches_remote(_job(
            location="Remote friendly (Denver, Colorado, United States) | United States"
        ))


class TestFilterJobs:
    def test_filters_combined(self):
        jobs = [
            _job("Data Engineer", location="Worldwide"),               # ✓
            _job("Marketing Manager", location="Worldwide"),           # ✗ role
            _job("Analytics Engineer", location="US Only"),            # ✗ region-locked
            _job("Data Platform Engineer", location="Asia"),           # ✗ asia not in include
            _job("Senior Data Engineer", location="Taiwan only"),      # ✓ Taiwan exception
            _job("Data Scientist", location="Hybrid - Berlin"),        # ✗ hybrid
            _job("Data Engineer", location="Remote"),                  # ✓ generic remote
        ]
        result = filter_jobs(jobs)
        assert len(result) == 3
        titles = {j.title for j in result}
        assert titles == {"Data Engineer", "Senior Data Engineer"}
