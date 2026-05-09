import sys

from job_scraper.models import Job
from job_scraper.scrapers.base import BaseScraper


class WelcomeToTheJungleScraper(BaseScraper):
    """Welcome To The Jungle — currently a stub.

    The public site is a Next.js app that streams job results via React Server
    Components; the SSR HTML at /en/jobs?... contains zero <a href="/jobs/...">
    nodes. The /api/v1/algolia/jobs endpoint hinted at in the brief returns
    HTTP 404 to anonymous POSTs and the page does not expose Algolia
    appId/apiKey for direct querying. Without a headless browser there is no
    reliable way to harvest listings, so this scraper returns [].

    Re-investigation paths if this is needed later:
      * Inspect a logged-in browser session for the real search endpoint
        (some WTTJ deployments use /api/v1/search-engine/v2/jobs).
      * Use the partner Algolia indexes published with each company page
        (https://www.welcometothejungle.com/en/companies/<slug>) which DO
        ship Algolia keys in their bundle.
      * Switch to playwright/headless-chromium and scrape the rendered page.
    """

    name = "wttj"

    def fetch(self) -> list[Job]:
        print(
            "  [wttj] stub — site requires JS rendering and no public API is reachable; returning []",
            file=sys.stderr,
        )
        return []

    def parse(self, data) -> list[Job]:  # noqa: ARG002 - kept for BaseScraper contract
        return []
