from typing import Optional
from datetime import datetime

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

        html_content = self._build_html(jobs)

        if not subject:
            subject = f"Remote PM/PO Job Digest - {len(jobs)} matches"

        params = {
            "from": self.config.email_from,
            "to": self.config.email_to,
            "subject": subject,
            "html": html_content,
        }

        if self.config.resend_api_key and self.config.resend_api_key != "placeholder_update_me":
            result = resend.Emails.send(params=params)
            print(f"Email sent: {result}")
            return result
        else:
            print(f"[DRY RUN] Would send email: {params}")
            return {"dry_run": True}

    def _build_html(self, jobs: list) -> str:
        today = datetime.now().strftime("%B %d, %Y")

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; background: #ffffff; }}
    .header {{ background: #4a5568; color: white; padding: 24px 20px; text-align: center; margin-bottom: 20px; }}
    .header h1 {{ margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 0.3px; }}
    .header p {{ margin: 6px 0 0; opacity: 0.85; font-size: 13px; font-weight: 400; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ padding: 10px 12px; text-align: left; font-size: 11px; font-weight: 600; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0; }}
    td {{ padding: 14px 12px; vertical-align: middle; border-bottom: 1px solid #f0f0f0; font-size: 13px; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f7fafc; }}
    .title {{ font-weight: 600; color: #2d3748; }}
    .company {{ font-size: 12px; color: #718096; margin-top: 3px; }}
    .location {{ color: #4a5568; font-size: 13px; }}
    .badges {{ display: flex; gap: 5px; flex-wrap: wrap; margin-top: 6px; }}
    .badge {{ padding: 2px 7px; border-radius: 3px; font-size: 10px; font-weight: 600; }}
    .badge-remote {{ background: #c6f6d5; color: #276749; }}
    .badge-new {{ background: #bee3f8; color: #2b6cb0; }}
    .badge-health {{ background: #feebc8; color: #c05621; }}
    .badge-salary {{ background: #e9d8fd; color: #6b46c1; }}
    .posted {{ color: #a0aec0; font-size: 12px; }}
    .apply-btn {{ display: inline-block; background: #4a5568; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 500; white-space: nowrap; }}
    .apply-btn:hover {{ background: #2d3748; }}
    .footer {{ text-align: center; padding: 20px; color: #a0aec0; font-size: 11px; margin-top: 20px; border-top: 1px solid #e2e8f0; }}
    .footer a {{ color: #4a5568; text-decoration: none; }}
</style>
</head>
<body>
    <div class="header">
        <h1>Remote PM/PO Job Digest</h1>
        <p>{today} | {len(jobs)} matching jobs</p>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width:32%">Role & Company</th>
                <th style="width:28%">Location</th>
                <th style="width:12%">Last Posted</th>
                <th style="width:28%"></th>
            </tr>
        </thead>
        <tbody>
"""

        for job in jobs[:25]:
            posted_str = ""
            if job.posted_at:
                try:
                    days = (datetime.utcnow() - job.posted_at.replace(tzinfo=None)).days
                    if days == 0:
                        posted_str = "Today"
                    elif days == 1:
                        posted_str = "Yesterday"
                    elif days <= 7:
                        posted_str = f"{days}d ago"
                    elif days <= 14:
                        posted_str = "1w ago"
                    elif days <= 30:
                        posted_str = f"{days // 7}w ago"
                    else:
                        posted_str = job.posted_at.strftime("%b %d")
                except:
                    posted_str = ""

            badges = ""
            if job.remote_type.value == "remote_us":
                badges += '<span class="badge badge-remote">Remote</span>'
            if posted_str in ["Today", "Yesterday"]:
                badges += '<span class="badge badge-new">Fresh</span>'
            if any("healthcare" in r.lower() for r in job.score_reasons):
                badges += '<span class="badge badge-health">Healthcare</span>'
            if job.salary_min and job.salary_max:
                badges += f'<span class="badge badge-salary">${job.salary_min // 1000}k-${job.salary_max // 1000}k</span>'

            html += f"""
            <tr>
                <td>
                    <div class="title">{job.title}</div>
                    <div class="company">{job.company}</div>
                    <div class="badges">{badges}</div>
                </td>
                <td class="location">{job.location[:35]}</td>
                <td class="posted">{posted_str}</td>
                <td><a href="{job.apply_url}" class="apply-btn">Apply</a></td>
            </tr>
"""

        html += """
        </tbody>
    </table>

    <div class="footer">
        <p>Sent by Job Aggregator | Mon-Fri | <a href="#">Preferences</a> | <a href="#">Unsubscribe</a></p>
    </div>
</body>
</html>
"""
        return html
