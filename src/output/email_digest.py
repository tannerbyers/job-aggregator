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
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 700px; margin: 0 auto; padding: 15px; background: #f8f9fa; }}
    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 15px; }}
    .header h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
    .header p {{ margin: 5px 0 0; opacity: 0.9; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    th {{ background: #f8f9fa; padding: 10px 12px; text-align: left; font-size: 11px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e9ecef; }}
    td {{ padding: 12px; vertical-align: middle; border-bottom: 1px solid #f0f0f0; font-size: 13px; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover {{ background: #fafafa; }}
    .title {{ font-weight: 600; color: #1a1a1a; }}
    .company {{ font-size: 12px; color: #666; margin-top: 2px; }}
    .location {{ color: #444; font-size: 13px; }}
    .badges {{ display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px; }}
    .badge {{ padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; }}
    .badge-remote {{ background: #e8f5e9; color: #2e7d32; }}
    .badge-new {{ background: #e3f2fd; color: #1565c0; }}
    .badge-health {{ background: #fce4ec; color: #c2185b; }}
    .badge-salary {{ background: #fff3e0; color: #e65100; }}
    .posted {{ color: #888; font-size: 12px; }}
    .apply-btn {{ display: inline-block; background: #667eea; color: white; padding: 8px 16px; border-radius: 5px; text-decoration: none; font-size: 12px; font-weight: 500; }}
    .apply-btn:hover {{ background: #5a6fd6; }}
    .footer {{ text-align: center; padding: 15px; color: #999; font-size: 11px; margin-top: 15px; }}
    .footer a {{ color: #667eea; text-decoration: none; }}
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
                <th style="width:35%">Role & Company</th>
                <th style="width:30%">Location</th>
                <th style="width:15%">Last Posted</th>
                <th style="width:20%"></th>
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
                badges += '<span class="badge badge-remote">Remote US</span>'
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
        <p>Sent by Job Aggregator | Matches updated Mon-Fri | <a href="#">Manage preferences</a> | <a href="#">Unsubscribe</a></p>
    </div>
</body>
</html>
"""
        return html
