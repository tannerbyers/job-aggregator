from datetime import datetime

from src.models.job import Job, RemoteType, EmploymentType
from src.output.kendall_email import EmailDigest


def test_kendall_email_includes_apply_button():
    job = Job(
        job_id="test1",
        company="TestCo",
        title="Product Manager",
        location="Remote - United States",
        remote_type=RemoteType.REMOTE_US,
        employment_type=EmploymentType.FULL_TIME,
        apply_url="https://example.com/job/1",
        source="test",
        posted_at=datetime.utcnow(),
    )

    email = EmailDigest()
    html = email._build_html([job], total_scanned=1)

    assert '<a href="https://example.com/job/1" class="apply-btn">Apply</a>' in html
