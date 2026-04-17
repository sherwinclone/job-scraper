from job_scraper.scrapers.remoteok import RemoteOKScraper
from job_scraper.scrapers.weworkremotely import WeWorkRemotelyScraper
from job_scraper.scrapers.remotive import RemotiveScraper
from job_scraper.scrapers.himalayas import HimalayasScraper
from job_scraper.scrapers.one04 import One04Scraper
from job_scraper.scrapers.jobspy_scraper import JobSpyScraper


def get_all_scrapers():
    return [RemoteOKScraper(), WeWorkRemotelyScraper(), RemotiveScraper(), HimalayasScraper(), One04Scraper(), JobSpyScraper()]
