#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

from src.config import get_config
from src.models.candidate import CandidateConfig
from src.models.job import Job
from src.matching.filters import JobFilter
from src.matching.scoring import JobScorer
from src.matching.dedupe import JobDedupe
from src.sources.greenhouse import GreenhouseFetcher
from src.sources.remoteok import RemoteOKFetcher
from src.output.email_digest import EmailDigest


def load_source_registry(path: Path) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def load_candidate_config() -> CandidateConfig:
    return CandidateConfig()


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
    print(f"[{datetime.utcnow().isoformat()}] Starting job digest run")

    config = get_config()
    data_dir = config.data_dir

    registry = load_source_registry(data_dir / "source_registry.json")
    candidate_config = load_candidate_config()

    print(f"Loaded {len(registry)} companies from registry")

    jobs = fetch_all_jobs(registry)
    print(f"Fetched {len(jobs)} raw jobs")

    filter = JobFilter(candidate_config)
    scorer = JobScorer(candidate_config)

    filtered_jobs = []
    for job in jobs:
        should_include, reason = filter.should_include(job)
        if should_include:
            score, reasons = scorer.score(job)
            job.score = score
            job.score_reasons = reasons
            filtered_jobs.append(job)

    print(f"Filtered to {len(filtered_jobs)} relevant jobs")

    dedupe = JobDedupe(data_dir / "jobs_seen.json")
    new_jobs = dedupe.filter_new(iter(filtered_jobs))
    print(f"New jobs after dedupe: {len(new_jobs)}")

    if not new_jobs:
        print("No new jobs, exiting")
        return

    new_jobs.sort(key=lambda j: j.score, reverse=True)

    dedupe.mark_seen_batch(new_jobs)

    email = EmailDigest()
    email.send_digest(new_jobs)

    print(f"Sent digest with {len(new_jobs)} jobs")


if __name__ == "__main__":
    main()
