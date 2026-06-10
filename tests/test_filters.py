import pytest

from src.models.candidate import CandidateConfig
from src.models.job import Job, RemoteType, EmploymentType
from src.matching.filters import JobFilter


@pytest.fixture
def config():
    return CandidateConfig()


@pytest.fixture
def job_filter(config):
    return JobFilter(config)


def test_include_exact_pm_title(job_filter):
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
    should_include, _ = job_filter.should_include(job)
    assert should_include


def test_include_product_owner(job_filter):
    job = Job(
        job_id="test2",
        company="TestCo",
        title="Product Owner",
        location="Remote",
        remote_type=RemoteType.REMOTE_US,
        employment_type=EmploymentType.FULL_TIME,
        apply_url="https://example.com/job/2",
        source="test",
    )
    should_include, _ = job_filter.should_include(job)
    assert should_include


def test_exclude_intern(job_filter):
    job = Job(
        job_id="test3",
        company="TestCo",
        title="Product Manager Intern",
        location="Remote - United States",
        remote_type=RemoteType.REMOTE_US,
        employment_type=EmploymentType.INTERNSHIP,
        apply_url="https://example.com/job/3",
        source="test",
    )
    should_include, _ = job_filter.should_include(job)
    assert not should_include


def test_exclude_vp(job_filter):
    job = Job(
        job_id="test4",
        company="TestCo",
        title="VP of Product",
        location="Remote - United States",
        remote_type=RemoteType.REMOTE_US,
        employment_type=EmploymentType.FULL_TIME,
        apply_url="https://example.com/job/4",
        source="test",
    )
    should_include, _ = job_filter.should_include(job)
    assert not should_include


def test_exclude_hybrid(job_filter):
    job = Job(
        job_id="test5",
        company="TestCo",
        title="Product Manager",
        location="Hybrid - New York",
        remote_type=RemoteType.HYBRID,
        employment_type=EmploymentType.FULL_TIME,
        apply_url="https://example.com/job/5",
        source="test",
    )
    should_include, reason = job_filter.should_include(job)
    assert not should_include


def test_exclude_wrong_country(job_filter):
    job = Job(
        job_id="test6",
        company="TestCo",
        title="Product Manager",
        location="Remote - Canada",
        remote_type=RemoteType.REMOTE_OTHER,
        employment_type=EmploymentType.FULL_TIME,
        apply_url="https://example.com/job/6",
        source="test",
    )
    should_include, _ = job_filter.should_include(job)
    assert not should_include
