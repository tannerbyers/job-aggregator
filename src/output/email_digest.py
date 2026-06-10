import os
from typing import Optional

import resend

from src.config import get_config


class EmailDigest:
    def __init__(self):
        self.config = get_config()
        if self.config.resend_api_key:
            resend.api_key = self.config.resend_api_key

    def send_digest(
        self,
        jobs: list,
        subject: Optional[str] = None,
        top_matches: Optional[list] = None,
        new_remote_us: Optional[list] = None,
        salary_visible: Optional[list] = None,
    ) -> dict:
        if not self.config.email_to:
            raise ValueError("EMAIL_TO not configured")

        if not jobs:
            print("No jobs to send, skipping email")
            return {"skipped": "no jobs"}

        html_content = self._build_html(jobs, top_matches, new_remote_us, salary_visible)

        if not subject:
            subject = f"Remote PM/PO Job Digest - {len(jobs)} matches"

        params = {
            "from": self.config.email_from or "jobs@resend.dev",
            "to": self.config.email_to,
            "subject": subject,
            "html": html_content,
        }

        if self.config.resend_api_key and self.config.resend_api_key != "placeholder_update_me":
            return resend.Emails.send(**params)
        else:
            print(f"[DRY RUN] Would send email: {params}")
            return {"dry_run": True}

    def _build_html(self, jobs: list, top_matches: Optional[list], new_remote_us: Optional[list], salary_visible: Optional[list]) -> str:
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1>Remote PM/PO Job Digest</h1>
            <p>Here are today's matching jobs.</p>
        """

        for job in jobs[:25]:
            html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 8px;">
                <h3 style="margin: 0 0 10px;">{job.title} at {job.company}</h3>
                <p style="margin: 5px 0;">
                    <strong>Location:</strong> {job.location}<br>
                    <strong>Score:</strong> {job.score}<br>
                """
            if job.salary_min and job.salary_max:
                html += f'<strong>Salary:</strong> ${job.salary_min:,} - ${job.salary_max:,}<br>'
            elif job.salary_min:
                html += f'<strong>Salary:</strong> ${job.salary_min:,}+<br>'
            if job.score_reasons:
                html += f'<strong>Why:</strong> {" | ".join(job.score_reasons)}<br>'
            html += f"""
                <a href="{job.apply_url}">Apply</a> | Source: {job.source}
                </p>
            </div>
            """

        html += """
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="color: #666; font-size: 12px;">
            Sent by Job Aggregator | <a href="#">Unsubscribe</a>
        </p>
        </body>
        </html>
        """

        return html
