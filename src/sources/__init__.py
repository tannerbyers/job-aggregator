from abc import ABC, abstractmethod
from typing import Iterator
from src.models.job import Job


class BaseFetcher(ABC):
    def __init__(self, company_id: str, company_name: str):
        self.company_id = company_id
        self.company_name = company_name

    @abstractmethod
    def fetch_jobs(self) -> Iterator[Job]:
        raise NotImplementedError


from .greenhouse import GreenhouseFetcher
from .lever import LeverFetcher
from .remoteok import RemoteOKFetcher

__all__ = ["BaseFetcher", "GreenhouseFetcher", "LeverFetcher", "RemoteOKFetcher"]
