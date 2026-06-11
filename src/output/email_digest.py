import os
from typing import Optional
from datetime import datetime, timedelta

import resend

from src.config import get_config


def get_company_initials(company_name: str) -> str:
    words = company_name.split()
    if len(words) >= 2:
        return words[0][0] + words[1][0]
    return company_name[:2].upper()


def get_company_color(company_name: str) -> str:
    colors = [
        "#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe",
        "#00f2fe", "#43e97b", "#38f9d7", "#ff9a9e", "#a18cd1",
        "#fad0c4", "#ffecd2", "#c1dfc4", "#deecdd", "#c9d6ff",
    ]
    hash_val = sum(ord(c) for c in company_name)
    return colors[hash_val % len(colors)]


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

    def _build_html(self, jobs: list, top_matches: Optional[list], new_remote_us: Optional[list], salary_visible: Optional[list]) -> str:
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
    .stats {{ display: flex; justify-content: center; gap: 30px; margin: 15px 0; }}
    .stat {{ text-align: center; }}
    .stat-num {{ font-size: 24px; font-weight: 700; color: #667eea; }}
    .stat-label {{ font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    th {{ background: #f8f9fa; padding: 10px 12px; text-align: left; font-size: 11px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e9ecef; }}
    td {{ padding: 10px 12px; vertical-align: middle; border-bottom: 1px solid #f0f0f0; font-size: 13px; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover {{ background: #f8f9fa; }}
    .company-cell {{ display: flex; align-items: center; gap: 10px; }}
    .logo {{ width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: white; flex-shrink: 0; }}
    .title-text {{ font-weight: 600; color: #1a1a1a; line-height: 1.3; }}
    .company-text {{ font-size: 12px; color: #666; }}
    .score {{ font-weight: 700; color: #667eea; }}
    .score-high {{ color: #2e7d32; }}
    .score-med {{ color: #f57c00; }}
    .badges {{ display: flex; gap: 4px; flex-wrap: wrap; }}
    .badge {{ padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; }}
    .badge-remote {{ background: #e8f5e9; color: #2e7d32; }}
    .badge-new {{ background: #e3f2fd; color: #1565c0; }}
    .badge-health {{ background: #fce4ec; color: #c2185b; }}
    .badge-salary {{ background: #fff3e0; color: #e65100; }}
    .location {{ color: #666; font-size: 12px; }}
    .apply-btn {{ display: inline-block; background: #667eea; color: white; padding: 6px 14px; border-radius: 5px; text-decoration: none; font-size: 12px; font-weight: 500; white-space: nowrap; }}
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
                <th style="width:30%">Role & Company</th>
                <th style="width:30%">Location & Badges</th>
                <th style="width:25%">Why It Matched</th>
                <th style="width:15%"></th>
            </tr>
        </thead>
        <tbody>
"""

        for job in jobs[:25]:
            logo_color = get_company_color(job.company)
            initials = get_company_initials(job.company)
            days_ago = None
            if job.posted_at:
                try:
                    days_ago = (datetime.utcnow() - job.posted_at.replace(tzinfo=None)).days
                except:
                    days_ago = None

            html += f"""
            <tr>
                <td>
                    <div class="company-cell">
                        <div class="logo" style="background:{logo_color}">{initials}</div>
                        <div>
                            <div class="title-text">{job.title}</div>
                            <div class="company-text">{job.company}</div>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="location">{job.location[:30]}</div>
                    <div class="badges">"""
            if job.remote_type.value == "remote_us":
                html += '<span class="badge badge-remote">Remote US</span>'
            if days_ago is not None and days_ago <= 3:
                html += '<span class="badge badge-new">New!</span>'
            if any("healthcare" in r.lower() for r in job.score_reasons):
                html += '<span class="badge badge-health">Healthcare</span>'
            if job.salary_min and job.salary_max:
                html += f'<span class="badge badge-salary">${job.salary_min // 1000}k-${job.salary_max // 1000}k</span>'
            html += """</div>
                </td>
                <td>
                    <div style="font-size:11px;color:#888;margin-bottom:4px;">"""
            html += " | ".join(job.score_reasons[:3])
            html += """</div>
                    <div style="font-size:11px;color:#999;">"""
            if days_ago is not None:
                html += f"Posted {days_ago}d ago"
            html += """</div>
                </td>
                <td>
                    <a href="{job.apply_url}" class="apply-btn">Apply</a>
                </td>
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
