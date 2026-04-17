from dataclasses import dataclass, field


@dataclass
class Job:
    id: str
    platform: str
    title: str
    company: str
    url: str
    tags: list[str] = field(default_factory=list)
    salary: str | None = None
    location: str | None = None
    posted_at: str | None = None
