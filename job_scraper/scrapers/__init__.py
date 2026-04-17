from job_scraper.scrapers.remoteok import RemoteOKScraper
from job_scraper.scrapers.weworkremotely import WeWorkRemotelyScraper
from job_scraper.scrapers.remotive import RemotiveScraper


def get_all_scrapers():
    return [RemoteOKScraper(), WeWorkRemotelyScraper(), RemotiveScraper()]
