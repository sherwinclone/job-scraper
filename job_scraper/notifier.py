import time


def format_job_message(job: dict) -> str:
    lines = [f"🆕 {job['title']} @ {job['company']}"]
    if job.get("salary"):
        lines.append(f"💰 {job['salary']}")
    if job.get("location"):
        lines.append(f"🌏 {job['location']}")
    if job.get("tags"):
        lines.append(f"🏷 {job['tags']}")
    lines.append(f"🔗 {job['url']}")
    return "\n".join(lines)


def notify_jobs(jobs: list[dict], store) -> int:
    try:
        from tg_notify import send
    except ImportError:
        print("tg-notify not installed. Skipping notifications.")
        return 0

    count = 0
    for job in jobs:
        msg = format_job_message(job)
        try:
            send(msg)
            store.mark_notified(job["id"])
            count += 1
            time.sleep(1)
        except Exception as e:
            print(f"Failed to notify {job['id']}: {e}")
    return count
