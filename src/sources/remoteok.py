import hashlib
from datetime import datetime
from typing import Iterator

import requests

from src.models.job import Job, RemoteType, EmploymentType
from src.sources import BaseFetcher


class RemoteOKFetcher(BaseFetcher):
    BASE_URL = "https://remoteok.com/api"

    INCLUDE_TERMS = ["product", "project", "program", "delivery", "scrum", "agile", "business analyst"]
    EXCLUDE_TERMS = ["engineer", "developer", "designer", "data scientist", "marketing", "sales"]

    def fetch_jobs(self) -> Iterator[Job]:
        try:
            headers = {"User-Agent": "Job Aggregator/1.0"}
            response = requests.get(self.BASE_URL, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            for job_data in data:
                if not isinstance(job_data, dict):
                    continue
                job = self._parse_job(job_data)
                if job:
                    yield job
        except requests.RequestException as e:
            print(f"Error fetching RemoteOK jobs: {e}")

    def _parse_job(self, job_data: dict) -> Optional[Job]:
        title = job_data.get("h1") or job_data.get("title", "")
        if not title:
            return None

        title_lower = title.lower()
        if not any(term in title_lower for term in self.INCLUDE_TERMS):
            return None
        if any(term in title_lower for term in self.EXCLUDE_TERMS):
            return None

        company = job_data.get("company", "")
        location = job_data.get("location", "Remote")
        apply_url = job_data.get("url", "")
        job_id = self._generate_job_id(company, title, location, apply_url)

        salary_range = self._parse_salary(job_data.get("salary"))

        return Job(
            job_id=job_id,
            company=company,
            title=title,
            location=location,
            remote_type=RemoteType.REMOTE_US,
            employment_type=EmploymentType.FULL_TIME,
            salary_min=salary_range[0],
            salary_max=salary_range[1],
            apply_url=f"https://remoteok.com{apply_url}" if apply_url.startswith("/") else apply_url,
            source="remoteok",
            posted_at=self._parse_posted_at(job_data),
            first_seen_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
        )

    def _generate_job_id(self, company: str, title: str, location: str, url: str) -> str:
        raw = f"{company}-{title}-{location}-{url}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def _parse_salary(self, salary_data) -> tuple[Optional[int], Optional[int]]:
        if not salary_data:
            return None, None
        if isinstance(salary_data, str):
            numbers = [int(s) for s in salary_data.replace(",", "").split() if s.isdigit()]
            if len(numbers) >= 2:
                return numbers[0], numbers[1]
            elif numbers:
                return numbers[0], None
        return None, None

    def _parse_posted_at(self, job_data: dict) -> Optional[datetime]:
        posted_str = job_data.get("date")
        if posted_str:
            try:
                return datetime.fromisoformat(posted_str.replace("Z", "+00:00"))
            except ValueError:
                pass
        return None
