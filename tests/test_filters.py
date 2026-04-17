from job_scraper.models import Job
from job_scraper.filters import matches_role, matches_timezone, filter_jobs


def _job(title="Data Engineer", tags=None, location=None):
    return Job(
        id="test:1", platform="test", title=title, company="TestCo",
        url="https://example.com", tags=tags or [], salary=None,
        location=location, posted_at=None,
    )


class TestMatchesRole:
    def test_data_engineer_title(self):
        assert matches_role(_job("Senior Data Engineer"))

    def test_backend_engineer_title(self):
        assert matches_role(_job("Backend Engineer - Python"))

    def test_irrelevant_title(self):
        assert not matches_role(_job("Marketing Manager"))

    def test_matches_via_tags(self):
        assert matches_role(_job("Software Engineer", tags=["python", "spark"]))

    def test_case_insensitive(self):
        assert matches_role(_job("ANALYTICS ENGINEER"))

    def test_databricks_tag(self):
        assert matches_role(_job("Engineer", tags=["databricks"]))


class TestMatchesTimezone:
    def test_worldwide(self):
        assert matches_timezone(_job(location="Worldwide"))

    def test_anywhere(self):
        assert matches_timezone(_job(location="Anywhere in the World"))

    def test_asia(self):
        assert matches_timezone(_job(location="Asia, Europe"))

    def test_empty_location(self):
        assert matches_timezone(_job(location=None))

    def test_empty_string_location(self):
        assert matches_timezone(_job(location=""))

    def test_us_only_excluded(self):
        assert not matches_timezone(_job(location="US Only"))

    def test_europe_only_excluded(self):
        assert not matches_timezone(_job(location="Europe Only"))

    def test_specific_asia_country(self):
        assert matches_timezone(_job(location="Singapore"))

    def test_americas_excluded(self):
        assert not matches_timezone(_job(location="Americas Only"))


class TestFilterJobs:
    def test_filters_combined(self):
        jobs = [
            _job("Data Engineer", location="Worldwide"),
            _job("Marketing Manager", location="Worldwide"),
            _job("Backend Developer", location="US Only"),
            _job("Python Developer", location="Asia"),
        ]
        result = filter_jobs(jobs)
        assert len(result) == 2
        assert result[0].title == "Data Engineer"
        assert result[1].title == "Python Developer"
