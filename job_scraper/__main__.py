import sys
import time
from pathlib import Path

import typer

from job_scraper.filters import filter_jobs
from job_scraper.notifier import notify_jobs
from job_scraper.scrapers import get_all_scrapers
from job_scraper.store import Store

app = typer.Typer(help="Remote job scraper for Data/Backend roles")

DEFAULT_DB = Path(__file__).parent.parent / "data" / "jobs.db"


@app.command()
def scrape(
    db: Path = typer.Option(DEFAULT_DB, help="SQLite database path"),
    notify: bool = typer.Option(False, help="Send new jobs to Telegram"),
):
    """Scrape all platforms, filter, and store new jobs."""
    store = Store(db)
    scrapers = get_all_scrapers()
    total_new = 0

    for scraper in scrapers:
        try:
            print(f"[{scraper.name}] Fetching...", file=sys.stderr)
            raw_jobs = scraper.fetch()
            filtered = filter_jobs(raw_jobs)
            new_count = store.save_jobs(filtered)
            total_new += new_count
            print(
                f"[{scraper.name}] {len(raw_jobs)} raw → {len(filtered)} matched → {new_count} new",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"[{scraper.name}] Error: {e}", file=sys.stderr)
        time.sleep(2)

    print(f"\nTotal: {total_new} new jobs saved", file=sys.stderr)

    if notify and total_new > 0:
        unnotified = store.get_unnotified_jobs()
        notified = notify_jobs(unnotified, store)
        print(f"Notified: {notified} jobs sent to Telegram", file=sys.stderr)


@app.command("list")
def list_jobs(
    db: Path = typer.Option(DEFAULT_DB, help="SQLite database path"),
    days: int = typer.Option(7, help="Show jobs from last N days"),
):
    """List recent jobs."""
    store = Store(db)
    jobs = store.get_recent_jobs(days=days)

    if not jobs:
        typer.echo("No jobs found.")
        return

    for i, j in enumerate(jobs, 1):
        typer.echo(f"\n{'─' * 60}")
        typer.echo(f"  {i}. {j['title']} @ {j['company']}")
        if j["salary"]:
            typer.echo(f"     💰 {j['salary']}")
        if j["location"]:
            typer.echo(f"     🌏 {j['location']}")
        if j["tags"]:
            typer.echo(f"     🏷  {j['tags']}")
        typer.echo(f"     🔗 {j['url']}")

    typer.echo(f"\n{'─' * 60}")
    typer.echo(f"Total: {len(jobs)} jobs in last {days} days")


@app.command()
def stats(
    db: Path = typer.Option(DEFAULT_DB, help="SQLite database path"),
):
    """Show database statistics."""
    store = Store(db)
    s = store.get_stats()
    typer.echo(f"Total jobs: {s['total_jobs']}")
    if s["by_platform"]:
        typer.echo("\nBy platform:")
        for platform, count in s["by_platform"].items():
            typer.echo(f"  {platform}: {count}")


@app.command("notify")
def send_notify(
    db: Path = typer.Option(DEFAULT_DB, help="SQLite database path"),
):
    """Send un-notified jobs to Telegram."""
    store = Store(db)
    unnotified = store.get_unnotified_jobs()
    if not unnotified:
        typer.echo("No new jobs to notify.")
        return
    notified = notify_jobs(unnotified, store)
    typer.echo(f"Sent {notified} jobs to Telegram.")


if __name__ == "__main__":
    app()
