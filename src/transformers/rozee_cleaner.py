from src.utils.logger import get_logger
from utils import handle_errors
from .main_transformer import BaseCleaner
from datetime import datetime, timedelta
from config.settings import TRANSFORMERS
from typing import Dict, Any, Optional

logger = get_logger(__name__)
rozee_cfg = TRANSFORMERS["rozee"]


class RozeeCleaner(BaseCleaner):
    @staticmethod
    @handle_errors
    def calculate_apply_before(posted_date: Optional[str]) -> Optional[str]:
        if not posted_date:
            return None
        posted_dt = datetime.fromisoformat(posted_date)
        apply_before_dt = posted_dt + timedelta(days=10)
        return apply_before_dt.isoformat()

    @handle_errors
    def transform(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cleaned = job.copy()
        cleaned = self.clean_basic_fields(cleaned)

        # Salary parsing
        salary = cleaned.get("salary")
        if salary:
            min_sal, max_sal = self.clean_salary(str(salary))
            cleaned["min_salary"] = min_sal
            cleaned["max_salary"] = max_sal
        else:
            cleaned["min_salary"] = None
            cleaned["max_salary"] = None

        # Skills parsing
        skills = cleaned.get("skills")
        if skills:
            if isinstance(skills, str):
                skills_list = [s.strip() for s in skills.split(',') if s.strip()]
            else:
                skills_list = skills

            soft_skills, core_skills = self.filter_skills(skills_list)
            cleaned["soft_skills"] = soft_skills
            cleaned["core_skills"] = core_skills
            cleaned["skill_count"] = len(core_skills)
        else:
            cleaned["soft_skills"] = []
            cleaned["core_skills"] = []
            cleaned["skill_count"] = 0

        # Date parsing
        posted_date_str = job.get("posted_date")
        if posted_date_str:
            parsed_date = self.parse_date(str(posted_date_str))
            cleaned["posted_date"] = parsed_date

            if parsed_date:
                cleaned["apply_before"] = self.calculate_apply_before(parsed_date)
            else:
                cleaned["apply_before"] = None
        else:
            cleaned["posted_date"] = None
            cleaned["apply_before"] = None

        cleaned["scraped_at"] = datetime.now().isoformat()
        cleaned["source"] = "rozee"

        return cleaned