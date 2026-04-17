import pytest

REMOTEOK_RESPONSE = [
    {"legal": "https://remoteok.com"},
    {
        "id": "12345",
        "position": "Senior Data Engineer",
        "company": "DataCorp",
        "tags": ["python", "spark", "aws"],
        "location": "Worldwide",
        "salary_min": 120000,
        "salary_max": 160000,
        "url": "https://remoteok.com/remote-jobs/12345",
        "date": "2026-04-17T00:00:00+00:00",
    },
    {
        "id": "12346",
        "position": "Marketing Manager",
        "company": "AdCo",
        "tags": ["marketing", "seo"],
        "location": "US Only",
        "salary_min": 0,
        "salary_max": 0,
        "url": "https://remoteok.com/remote-jobs/12346",
        "date": "2026-04-16T00:00:00+00:00",
    },
]

REMOTIVE_RESPONSE = {
    "jobs": [
        {
            "id": 99001,
            "title": "Backend Engineer - Python",
            "company_name": "RemotePy",
            "url": "https://remotive.com/remote-jobs/99001",
            "tags": ["python", "django", "postgresql"],
            "salary": "$130k - $170k",
            "candidate_required_location": "Worldwide",
            "publication_date": "2026-04-17T10:00:00",
        },
        {
            "id": 99002,
            "title": "iOS Developer",
            "company_name": "AppCo",
            "url": "https://remotive.com/remote-jobs/99002",
            "tags": ["swift", "ios"],
            "salary": "",
            "candidate_required_location": "Americas",
            "publication_date": "2026-04-16T10:00:00",
        },
    ]
}

WWR_HTML = """\
<ul>
  <li class="new-listing-container feature">
    <a class="listing-link--unlocked" href="/remote-jobs/datacorp-data-engineer">
      <div class="new-listing paid-logo">
        <div class="new-listing__header">
          <h3 class="new-listing__header__title">
            <span class="new-listing__header__title__text">Data Engineer</span>
          </h3>
        </div>
        <p class="new-listing__company-name">DataCorp</p>
        <p class="new-listing__company-headquarters">Singapore</p>
        <div class="new-listing__categories">
          <p class="new-listing__categories__category">Full-Time</p>
          <p class="new-listing__categories__category">Asia</p>
        </div>
      </div>
    </a>
  </li>
  <li class="new-listing-container feature">
    <a class="listing-link--unlocked" href="/remote-jobs/designco-ux-designer">
      <div class="new-listing paid-logo">
        <div class="new-listing__header">
          <h3 class="new-listing__header__title">
            <span class="new-listing__header__title__text">UX Designer</span>
          </h3>
        </div>
        <p class="new-listing__company-name">DesignCo</p>
        <p class="new-listing__company-headquarters">New York, US</p>
        <div class="new-listing__categories">
          <p class="new-listing__categories__category">Full-Time</p>
          <p class="new-listing__categories__category">US Only</p>
        </div>
      </div>
    </a>
  </li>
</ul>
"""


@pytest.fixture
def remoteok_response():
    return REMOTEOK_RESPONSE


@pytest.fixture
def remotive_response():
    return REMOTIVE_RESPONSE


@pytest.fixture
def wwr_html():
    return WWR_HTML
