from abc import ABC, abstractmethod
from job_scraper.models import Job


class BaseScraper(ABC):
    name: str

    @abstractmethod
    def fetch(self) -> list[Job]:
        ...

    @abstractmethod
    def parse(self, data) -> list[Job]:
        ...
