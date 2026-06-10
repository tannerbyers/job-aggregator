import hashlib
import re
from datetime import datetime
from typing import Iterator, Optional
from urllib.parse import urlparse

import requests

from src.models.job import Job, RemoteType, EmploymentType
from src.sources import BaseFetcher


class GreenhouseFetcher(BaseFetcher):
    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(self, company_id: str, company_name: str, board_token: str):
        super().__init__(company_id, company_name)
        self.board_token = board_token

    def fetch_jobs(self) -> Iterator[Job]:
        url = f"{self.BASE_URL}/{self.board_token}/jobs?content=true"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            for job_data in data.get("jobs", []):
                yield self._parse_job(job_data)
        except requests.RequestException as e:
            print(f"Error fetching Greenhouse jobs for {self.company_name}: {e}")

    def _parse_job(self, job_data: dict) -> Job:
        location = job_data.get("location", {}).get("name", "Unknown")
        departments = job_data.get("departments", [])
        department = departments[0]["name"] if departments else None

        apply_url = job_data.get("absolute_url", "")
        job_id = self._generate_job_id(job_data.get("id"), apply_url)

        employment_type = self._parse_employment_type(job_data.get("metadata"))
        remote_type = self._parse_remote_type(location)

        return Job(
            job_id=job_id,
            external_id=str(job_data.get("id", "")),
            company=self.company_name,
            title=job_data.get("title", ""),
            department=department,
            location=location,
            remote_type=remote_type,
            employment_type=employment_type,
            description=job_data.get("content", ""),
            apply_url=apply_url,
            source="greenhouse",
            posted_at=self._parse_posted_at(job_data),
            first_seen_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
        )

    def _generate_job_id(self, external_id: str, apply_url: str) -> str:
        raw = f"{self.company_id}-{external_id}-{apply_url}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def _parse_remote_type(self, location: str) -> RemoteType:
        location_lower = location.lower()
        if any(kw in location_lower for kw in ["remote", "work from home", "distributed", "united states", "usa"]):
            if not any(kw in location_lower for kw in ["canada", "europe", "uk", "hybrid", "onsite"]):
                return RemoteType.REMOTE_US
            return RemoteType.REMOTE_OTHER
        if "hybrid" in location_lower:
            return RemoteType.HYBRID
        if "onsite" in location_lower or "on-site" in location_lower:
            return RemoteType.ONSITE
        return RemoteType.UNKNOWN

    def _parse_employment_type(self, metadata: Optional[list]) -> EmploymentType:
        if not metadata:
            return EmploymentType.UNKNOWN
        for item in metadata:
            if item.get("name", "").lower() == "employment type":
                value = item.get("value", "").lower()
                if "full" in value:
                    return EmploymentType.FULL_TIME
                elif "part" in value:
                    return EmploymentType.PART_TIME
                elif "contract" in value:
                    return EmploymentType.CONTRACT
        return EmploymentType.UNKNOWN

    def _parse_posted_at(self, job_data: dict) -> Optional[datetime]:
        updated_at = job_data.get("updated_at")
        if updated_at:
            try:
                return datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            except ValueError:
                pass
        return None
