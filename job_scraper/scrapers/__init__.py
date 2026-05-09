from job_scraper.scrapers.remoteok import RemoteOKScraper
from job_scraper.scrapers.weworkremotely import WeWorkRemotelyScraper
from job_scraper.scrapers.remotive import RemotiveScraper
from job_scraper.scrapers.himalayas import HimalayasScraper
from job_scraper.scrapers.one04 import One04Scraper
from job_scraper.scrapers.jobspy_scraper import JobSpyScraper
from job_scraper.scrapers.hitmarker import HitmarkerScraper
from job_scraper.scrapers.parlayjobs import ParlayJobsScraper
from job_scraper.scrapers.justremote import JustRemoteScraper
from job_scraper.scrapers.wttj import WelcomeToTheJungleScraper
from job_scraper.scrapers.workingnomads import WorkingNomadsScraper


def get_all_scrapers():
    return [
        RemoteOKScraper(),
        WeWorkRemotelyScraper(),
        RemotiveScraper(),
        HimalayasScraper(),
        One04Scraper(),
        JobSpyScraper(),
        HitmarkerScraper(),
        ParlayJobsScraper(),
        JustRemoteScraper(),
        WelcomeToTheJungleScraper(),
        WorkingNomadsScraper(),
    ]
