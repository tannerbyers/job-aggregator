import hashlib
from datetime import datetime
from typing import Iterator

import requests

from src.models.job import Job, RemoteType, EmploymentType
from src.sources import BaseFetcher


class LeverFetcher(BaseFetcher):
    BASE_URL = "https://api.lever.co/v0/postings"

    def __init__(self, company_id: str, company_name: str, lever_slug: str):
        super().__init__(company_id, company_name)
        self.lever_slug = lever_slug

    def fetch_jobs(self) -> Iterator[Job]:
        url = f"{self.BASE_URL}/{self.lever_slug}?mode=json"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                for job_data in data:
                    yield self._parse_job(job_data)
        except requests.RequestException as e:
            print(f"Error fetching Lever jobs for {self.company_name}: {e}")

    def _parse_job(self, job_data: dict) -> Job:
        location = job_data.get("location", "Unknown")
        apply_url = job_data.get("applyUrl", "")
        job_id = self._generate_job_id(job_data.get("id"), apply_url)

        remote_type = self._parse_remote_type(location)

        return Job(
            job_id=job_id,
            external_id=str(job_data.get("id", "")),
            company=self.company_name,
            title=job_data.get("title", ""),
            department=job_data.get("departments", [{}])[0].get("title") if job_data.get("departments") else None,
            location=location,
            remote_type=remote_type,
            employment_type=EmploymentType.FULL_TIME,
            description=job_data.get("description"),
            apply_url=apply_url,
            source="lever",
            posted_at=self._parse_posted_at(job_data),
            first_seen_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
        )

    def _generate_job_id(self, external_id: str, apply_url: str) -> str:
        raw = f"{self.company_id}-{external_id}-{apply_url}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def _parse_remote_type(self, location: str) -> RemoteType:
        location_lower = location.lower()

        if not any(kw in location_lower for kw in ["remote", "work from home", "distributed"]):
            if "hybrid" in location_lower:
                return RemoteType.HYBRID
            if "onsite" in location_lower or "on-site" in location_lower:
                return RemoteType.ONSITE
            return RemoteType.UNKNOWN

        non_us_keywords = [
            "canada", "europe", "uk", "united kingdom", "germany", "france", "ireland",
            "netherlands", "spain", "italy", "sweden", "norway", "denmark", "finland",
            "poland", "czech", "hungary", "romania", "bulgaria", "ukraine", "russia",
            "australia", "new zealand", "singapore", "japan", "china", "india", "brazil",
            "mexico", "argentina", "chile", "colombia", "uae", "united arab emirates",
            "dubai", "israel", "south africa", "kenya", "egypt", "nigeria",
            "hong kong", "malaysia", "thailand", "indonesia", "philippines",
        ]

        us_only_keywords = ["united states", "usa", "us ", " us,"]

        has_non_us = any(kw in location_lower for kw in non_us_keywords)
        has_us_only = any(kw in location_lower for kw in us_only_keywords)

        if has_non_us and not has_us_only:
            return RemoteType.REMOTE_OTHER
        return RemoteType.REMOTE_US
