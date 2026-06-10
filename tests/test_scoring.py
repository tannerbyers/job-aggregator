import pytest
from datetime import datetime, timedelta

from src.models.candidate import CandidateConfig
from src.models.job import Job, RemoteType, EmploymentType
from src.matching.scoring import JobScorer


@pytest.fixture
def config():
    return CandidateConfig()


@pytest.fixture
def scorer(config):
    return JobScorer(config)


def test_remote_us_bonus(scorer):
    job = Job(
        job_id="test1",
        company="TestCo",
        title="Product Manager",
        location="Remote - United States",
        remote_type=RemoteType.REMOTE_US,
        employment_type=EmploymentType.FULL_TIME,
        apply_url="https://example.com/job/1",
        source="test",
    )
    score, reasons = scorer.score(job)
    assert score >= 40
    assert "Remote US" in reasons


def test_salary_visible_bonus(scorer):
    job = Job(
        job_id="test2",
        company="TestCo",
        title="Product Manager",
        location="Remote - United States",
        remote_type=RemoteType.REMOTE_US,
        employment_type=EmploymentType.FULL_TIME,
        salary_min=120000,
        salary_max=160000,
        apply_url="https://example.com/job/2",
        source="test",
    )
    score, reasons = scorer.score(job)
    assert score >= 55
    assert "Salary visible" in reasons


def test_recently_posted_bonus(scorer):
    job = Job(
        job_id="test3",
        company="TestCo",
        title="Product Manager",
        location="Remote - United States",
        remote_type=RemoteType.REMOTE_US,
        employment_type=EmploymentType.FULL_TIME,
        posted_at=datetime.utcnow() - timedelta(days=3),
        apply_url="https://example.com/job/3",
        source="test",
    )
    score, reasons = scorer.score(job)
    assert any("Recently posted" in r for r in reasons)


def test_minimum_score_threshold(scorer):
    job = Job(
        job_id="test4",
        company="TestCo",
        title="Product Manager",
        location="Remote - United States",
        remote_type=RemoteType.REMOTE_US,
        employment_type=EmploymentType.FULL_TIME,
        apply_url="https://example.com/job/4",
        source="test",
    )
    assert scorer.is_minimum_score(job, 70)


def test_below_minimum_score(scorer):
    job = Job(
        job_id="test5",
        company="TestCo",
        title="Product Analyst",
        location="Unknown",
        remote_type=RemoteType.UNKNOWN,
        employment_type=EmploymentType.UNKNOWN,
        apply_url="https://example.com/job/5",
        source="test",
    )
    assert not scorer.is_minimum_score(job, 70)
