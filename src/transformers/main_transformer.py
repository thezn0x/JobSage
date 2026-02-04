import re
from datetime import datetime, timedelta

from utils import handle_errors
from .soft_skills import SOFT_SKILLS_KEYWORDS
from src.utils.logger import get_logger
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json

logger = get_logger(__name__)

class BaseCleaner(ABC):
    def __init__(self, extractor_name: str):
        self.extractor_name = extractor_name

    @staticmethod
    @handle_errors
    def parse_date(date_str: str) -> Optional[str]:
        if not date_str:
            return None

        date_str = date_str.strip()
        try:
            date_obj = datetime.fromisoformat(date_str)
            return date_obj.isoformat()
        except ValueError:
            pass
        try:
            date_obj = datetime.strptime(date_str, "%b %d, %Y")
            date_obj = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            return date_obj.isoformat()
        except ValueError:
            pass
        relative = re.search(
            r'(\d+)\s+(hour|day|week|month)s?\s+ago',
            date_str,
            re.IGNORECASE
        )
        if relative:
            amount = int(relative.group(1))
            unit = relative.group(2).lower().rstrip('s')

            now = datetime.now()
            unit_map = {
                'hour': timedelta(hours=amount),
                'day': timedelta(days=amount),
                'week': timedelta(weeks=amount),
                'month': timedelta(days=amount * 30)
            }

            if unit in unit_map:
                date_obj = now - unit_map[unit]
                date_obj = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                return date_obj.isoformat()

        logger.warning(f"Could not parse Rozee date: {date_str}")
        return None

    @staticmethod
    def _clean_text(text: str) -> str:
        if text:
            return text.strip()
        return ""

    @handle_errors
    def clean_basic_fields(self, job: Dict[str, Any]) -> Dict[str, Any]:
        cleaned_job:dict = {"title": self._clean_text(job.get("title", "")),
                            "application_url": self._clean_text(job.get("url", "")),
                            "location": self._clean_text(job.get("location", "")),
                            "description": self._clean_text(job.get("description", "")),
                            "company": self._clean_text(job.get("company", "")),
                            "source": job.get("source", "unknown"),
                            "salary": job.get("salary"),
                            "salary_currency": "PKR",
                            "experience_text": job.get("experience_text"),
                            "min_experience": job.get("experience_years"),
                            "skills": job.get("skills", []),
                            "requirements": job.get("skills", [])}
        return cleaned_job

    @staticmethod
    @handle_errors
    def clean_salary(salary_str: str) -> tuple:
        if not salary_str:
            return None, None
        parts = salary_str.split("-")
        if len(parts) != 2:
            return None, None

        # Check if contains 'k' for thousands
        has_k = 'k' in parts[0].lower() or 'k' in parts[1].lower()

        # Clean and parse
        min_sal = parts[0].lower().replace("k", "").replace(",", "").strip()
        max_sal = parts[1].lower().replace("k", "").replace(",", "").strip()

        min_salary = int(min_sal) * (1000 if has_k else 1)
        max_salary = int(max_sal) * (1000 if has_k else 1)

        return min_salary, max_salary

    @staticmethod
    def filter_skills(skills: List[str]) -> tuple:
        if not skills:
            return [], []
        
        soft_skills = []
        core_skills = []
        
        for skill in skills:
            skill_lower = skill.lower().strip()
            if skill_lower in SOFT_SKILLS_KEYWORDS:
                soft_skills.append(skill_lower)
            else:
                core_skills.append(skill)
        
        return soft_skills, core_skills

    @handle_errors
    def clean_jobs(self, jobs: List) -> List[Dict[str, Any]]:
        logger.info(f"Starting clean_jobs() for {self.extractor_name}...")
        cleaned = []
        for job in jobs:
            cleaned_job = self.transform(job)
            if cleaned_job:
                cleaned.append(cleaned_job)
        return cleaned

    @abstractmethod
    def transform(self, job: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclass must implement transform()")
    
    @staticmethod
    @handle_errors
    def save_jobs(filename: str, jobs: List[Dict]) -> bool:
        logger.info(f"Saving {len(jobs)} jobs to {filename}...")
        # Remove None values
        _jobs = [job for job in jobs if job is not None]

        # Deduplicate by title, company, and location
        seen_jobs_criteria = set()
        deduplicated_jobs = []

        for job in _jobs:
            title = job.get("title", "").strip().lower()
            company = job.get("company", "").strip().lower()
            location = job.get("location", "").strip().lower()
            # A job is considered unique if it has all three criteria
            if title and company and location:
                job_criteria = (title, company, location)
                if job_criteria not in seen_jobs_criteria:
                    deduplicated_jobs.append(job)
                    seen_jobs_criteria.add(job_criteria)
                else:
                    logger.info(f"Skipping duplicate job based on title, company, location: {job.get('title', 'Unknown Title')} - {job.get('company', 'Unknown Company')} - {job.get('location', 'Unknown Location')}")
            else:
                logger.warning(f"Job missing title, company, or location, skipping for deduplication: {job.get('title', 'Unknown Title')}")

        with open(filename, "w") as f:
            json.dump(deduplicated_jobs, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(deduplicated_jobs)} unique jobs to {filename}. {len(_jobs) - len(deduplicated_jobs)} potential duplicates were removed.")
        return True