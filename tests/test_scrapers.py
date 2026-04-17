from job_scraper.scrapers.base import BaseScraper
from job_scraper.scrapers.remoteok import RemoteOKScraper
from job_scraper.scrapers.remotive import RemotiveScraper
from job_scraper.scrapers.weworkremotely import WeWorkRemotelyScraper

from tests.conftest import REMOTEOK_RESPONSE, REMOTIVE_RESPONSE, WWR_HTML


class TestRemoteOKScraper:
    def test_parse_jobs(self):
        scraper = RemoteOKScraper()
        jobs = scraper.parse(REMOTEOK_RESPONSE)
        assert len(jobs) == 2
        assert jobs[0].id == "remoteok:12345"
        assert jobs[0].title == "Senior Data Engineer"
        assert jobs[0].company == "DataCorp"
        assert jobs[0].platform == "remoteok"
        assert "python" in jobs[0].tags
        assert jobs[0].salary == "$120,000 - $160,000"
        assert jobs[0].location == "Worldwide"

    def test_skips_legal_entry(self):
        scraper = RemoteOKScraper()
        jobs = scraper.parse(REMOTEOK_RESPONSE)
        assert all(j.company != "" for j in jobs)

    def test_zero_salary_shows_none(self):
        scraper = RemoteOKScraper()
        jobs = scraper.parse(REMOTEOK_RESPONSE)
        assert jobs[1].salary is None


class TestRemotiveScraper:
    def test_parse_jobs(self):
        scraper = RemotiveScraper()
        jobs = scraper.parse(REMOTIVE_RESPONSE)
        assert len(jobs) == 2
        assert jobs[0].id == "remotive:99001"
        assert jobs[0].title == "Backend Engineer - Python"
        assert jobs[0].company == "RemotePy"
        assert jobs[0].salary == "$130k - $170k"
        assert jobs[0].location == "Worldwide"

    def test_empty_salary(self):
        scraper = RemotiveScraper()
        jobs = scraper.parse(REMOTIVE_RESPONSE)
        assert jobs[1].salary is None


class TestWeWorkRemotelyScraper:
    def test_parse_jobs(self):
        scraper = WeWorkRemotelyScraper()
        jobs = scraper.parse(WWR_HTML)
        assert len(jobs) == 2
        assert jobs[0].title == "Data Engineer"
        assert jobs[0].company == "DataCorp"
        assert jobs[0].platform == "weworkremotely"
        assert "weworkremotely.com" in jobs[0].url

    def test_extracts_location(self):
        scraper = WeWorkRemotelyScraper()
        jobs = scraper.parse(WWR_HTML)
        assert "Asia" in jobs[0].location
