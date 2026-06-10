import json
from datetime import datetime
from pathlib import Path
from typing import Iterator

from src.models.job import Job


class JobDedupe:
    def __init__(self, seen_file: Path):
        self.seen_file = seen_file
        self.seen_ids: set[str] = set()
        self._load()

    def _load(self):
        if self.seen_file.exists():
            with open(self.seen_file) as f:
                data = json.load(f)
                self.seen_ids = set(data.get("seen_job_ids", []))

    def _save(self):
        with open(self.seen_file, "w") as f:
            json.dump(
                {
                    "seen_job_ids": list(self.seen_ids),
                    "last_updated": datetime.utcnow().isoformat(),
                },
                f,
                indent=2,
            )

    def is_seen(self, job: Job) -> bool:
        return job.job_id in self.seen_ids

    def mark_seen(self, job: Job):
        self.seen_ids.add(job.job_id)

    def mark_seen_batch(self, jobs: list[Job]):
        for job in jobs:
            self.mark_seen(job)
        self._save()

    def filter_new(self, jobs: Iterator[Job]) -> list[Job]:
        new_jobs = []
        for job in jobs:
            if not self.is_seen(job):
                new_jobs.append(job)
        return new_jobs
