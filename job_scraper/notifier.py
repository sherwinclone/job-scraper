import os
import time

import httpx


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


def _send_telegram(text: str) -> bool:
    """Send message via Telegram Bot API directly."""
    token = os.environ.get("TG_BOT_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if not token or not chat_id:
        return False
    resp = httpx.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        timeout=10,
    )
    return resp.status_code == 200


def notify_jobs(jobs: list[dict], store) -> int:
    token = os.environ.get("TG_BOT_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if not token or not chat_id:
        print("TG_BOT_TOKEN or TG_CHAT_ID not set. Skipping notifications.")
        return 0

    count = 0
    for job in jobs:
        msg = format_job_message(job)
        try:
            if _send_telegram(msg):
                store.mark_notified(job["id"])
                count += 1
            else:
                print(f"Failed to notify {job['id']}")
            time.sleep(1)
        except Exception as e:
            print(f"Failed to notify {job['id']}: {e}")
    return count
