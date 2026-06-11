#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.config import get_config
from src.models.job import Job
from src.matching.kendall_scorer import hard_reject, score_kendall
from src.matching.dedupe import JobDedupe
from src.sources.greenhouse import GreenhouseFetcher
from src.sources.remoteok import RemoteOKFetcher
from src.output.kendall_email import EmailDigest


def load_source_registry(path: Path) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def load_kendall_profile(data_dir: Path) -> dict:
    profile_path = data_dir / "kendall_profile.json"
    if profile_path.exists():
        with open(profile_path) as f:
            return json.load(f)
    return {}


def load_kendall_feedback(data_dir: Path) -> dict:
    feedback_path = data_dir / "kendall_feedback.json"
    if feedback_path.exists():
        with open(feedback_path) as f:
            return json.load(f)
    return {"feedback": [], "adjustments": {}}


def should_send_email(profile: dict, data_dir: Path) -> bool:
    frequency = profile.get("frequency", "daily")

    if frequency == "daily":
        return True

    if frequency == "weekly":
        today = datetime.now(timezone.utc).weekday()
        return today == 0

    if frequency in ("every_2_days", "every_3_days"):
        last_send_file = data_dir / "last_send_date.json"
        days_interval = 2 if frequency == "every_2_days" else 3

        if not last_send_file.exists():
            return True

        with open(last_send_file) as f:
            data = json.load(f)
            last_send = datetime.fromisoformat(data["last_send"])
            days_since = (datetime.now(timezone.utc) - last_send).days
            return days_since >= days_interval

    if frequency == "paused":
        return False

    return True


def mark_email_sent(profile: dict, data_dir: Path):
    frequency = profile.get("frequency", "daily")

    if frequency in ("every_2_days", "every_3_days"):
        last_send_file = data_dir / "last_send_date.json"
        with open(last_send_file, "w") as f:
            json.dump({
                "last_send": datetime.now(timezone.utc).isoformat()
            }, f)


def fetch_all_jobs(registry: list[dict]) -> list[Job]:
    jobs = []

    for company in registry:
        if company.get("status") != "active":
            continue

        ats = company.get("ats")
        company_id = company.get("company_id")
        company_name = company.get("company_name")

        if ats == "greenhouse" and company.get("board_token"):
            fetcher = GreenhouseFetcher(
                company_id=company_id,
                company_name=company_name,
                board_token=company["board_token"],
            )
            for job in fetcher.fetch_jobs():
                jobs.append(job)

    remoteok_fetcher = RemoteOKFetcher(company_id="remoteok", company_name="RemoteOK")
    for job in remoteok_fetcher.fetch_jobs():
        jobs.append(job)

    return jobs


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Kendall's job digest")

    config = get_config()
    data_dir = config.data_dir

    registry = load_source_registry(data_dir / "source_registry.json")
    profile = load_kendall_profile(data_dir)
    feedback_data = load_kendall_feedback(data_dir)

    print(f"Loaded {len(registry)} companies from registry")

    if not should_send_email(profile, data_dir):
        print(f"Skipping - frequency set to '{profile.get('frequency', 'daily')}' and today is not a send day")
        return

    jobs = fetch_all_jobs(registry)
    total_scanned = len(jobs)
    print(f"Fetched {total_scanned} raw jobs")

    include_contract = profile.get("include_contract", True)
    adjustments = feedback_data.get("adjustments", {})

    filtered_jobs = []
    rejected_count = 0

    for job in jobs:
        rejected, reason = hard_reject(job, include_contract)
        if rejected:
            rejected_count += 1
            continue

        score, reasons, risks = score_kendall(job, profile, adjustments)
        job.score = score
        job.score_reasons = reasons
        job.risks = risks
        filtered_jobs.append(job)

    print(f"After hard rejects: {len(filtered_jobs)} jobs ({rejected_count} rejected)")

    dedupe = JobDedupe(data_dir / "jobs_seen.json")
    new_jobs = dedupe.filter_new(iter(filtered_jobs))
    print(f"New jobs after dedupe: {len(new_jobs)}")

    min_score = profile.get("minimum_score", 82)
    new_jobs = [j for j in new_jobs if j.score >= min_score]
    print(f"After minimum score filter (>={min_score}): {len(new_jobs)}")

    if not new_jobs:
        print("No strong matches today")
        return

    new_jobs.sort(key=lambda j: j.score, reverse=True)

    max_jobs = profile.get("daily_max_jobs", 5)
    final_jobs = new_jobs[:max_jobs]

    dedupe.mark_seen_batch(final_jobs)

    email = EmailDigest()
    try:
        email.send_digest(final_jobs, total_scanned=total_scanned)
        mark_email_sent(profile, data_dir)
        print(f"Sent digest with {len(final_jobs)} jobs (scanned {total_scanned} total)")
    except ValueError as e:
        print(f"Email not configured: {e}")
        print(f"Would have sent {len(final_jobs)} jobs:")
        for job in final_jobs[:10]:
            print(f"  - {job.title} at {job.company} (score: {job.score})")


if __name__ == "__main__":
    main()