import re
from typing import Optional

from src.models.job import Job, RemoteType, EmploymentType
from src.models.candidate import CandidateConfig


class JobFilter:
    def __init__(self, config: CandidateConfig):
        self.config = config

    def should_include(self, job: Job) -> tuple[bool, str]:
        if not self._check_title(job.title):
            return False, f"Title '{job.title}' excluded"

        if not self._check_remote(job):
            return False, f"Remote type '{job.remote_type}' not matching"

        if not self._check_employment_type(job):
            return False, f"Employment type '{job.employment_type}' not full-time"

        if not self._check_salary(job):
            return False, f"Salary below minimum ${self.config.min_salary:,}"

        return True, "Passed all filters"

    def _check_title(self, title: str) -> bool:
        title_lower = title.lower()

        if any(excl in title_lower for excl in self.config.excluded_titles):
            return False

        if any(incl in title_lower for incl in self.config.include_title_keywords):
            return True

        return False

    def _check_remote(self, job: Job) -> bool:
        if not self.config.remote_required:
            return True

        if job.remote_type == RemoteType.REMOTE_US:
            return True

        if job.remote_type == RemoteType.UNKNOWN:
            location_lower = job.location.lower()
            if any(kw in location_lower for kw in self.config.remote_include_keywords):
                if not any(kw in location_lower for kw in self.config.remote_exclude_keywords):
                    return True

        return False

    def _check_employment_type(self, job: Job) -> bool:
        return job.employment_type in [EmploymentType.FULL_TIME, EmploymentType.UNKNOWN]

    def _check_salary(self, job: Job) -> bool:
        if not self.config.min_salary:
            return True
        if job.salary_min and job.salary_min < self.config.min_salary:
            return False
        return True
