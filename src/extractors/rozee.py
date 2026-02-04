import re
from datetime import datetime
from utils import handle_errors
from .base import Extractor
from src.utils.logger import get_logger
from typing import Dict,Any,Union

# LOGGER
logger = get_logger(__name__)

class RozeeExtractor(Extractor):
    @handle_errors
    def extract(self,card) -> Union[bool,None,Dict[str,Any]]:
        job = {}
        # GET TITLE
        title_element = card.query_selector("div.jhead h3 a,h3 a")
        if not title_element:
            return None
        job["title"] = self.clean_text(title_element.inner_text())
        href = title_element.get_attribute("href")
        job["url"] = f"https://{href.lstrip('/')}" if href else None
        company_element = card.query_selector("div.cname a,div.jcompany a")
        job["company"] = self.clean_text(company_element.inner_text()) if company_element else None
        # GET LOCATION
        location = "Pakistan"
        cname_div = card.query_selector("div.cname")
        if cname_div:
            links = cname_div.query_selector_all("a")
            if len(links) > 1:
                parts = [self.clean_text(link.inner_text()) for link in links[1:] if self.clean_text(link.inner_text())]
                if parts:
                    location = ", ".join(parts)
        job["location"]=location
        # GET DESCRIPTION
        desc_element = card.query_selector("div.jbody")
        if desc_element:
            text = self.clean_text(desc_element.inner_text())
            job["description"] = text[:500]
        footer = card.query_selector("div.jfooter")
        if footer:
            text = self.clean_text(footer.inner_text())
            absolute_date = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}", text)
            relative_date = re.search(r"\d+\s+(day|days|week|weeks|month|months)\s+ago", text, re.I)
            if absolute_date:
                job["posted_date"] = absolute_date.group(0)
            elif relative_date:
                job["posted_date"] = relative_date.group(0)
        # GET SALARY
        salary_el = card.query_selector("span[data-toggle='tooltip'] > span:not([class])")
        if salary_el:
            salary_text = self.clean_text(salary_el.inner_text())
            if salary_text:
                job["salary"] = salary_text
        # GET EXPERIENCE
        exp_element = card.query_selector("span.func-area-drn")
        if exp_element:
            exp_text = self.clean_text(exp_element.inner_text())
            job["experience_text"] = exp_text
            match = re.search(r"(\d)\s(year|years)",exp_text,re.I)
            if match:
                job["experience_years"] = int(match.group(1))
        # GET SKILLS
        skills = []
        for s in card.query_selector_all("span.label"):
            value = self.clean_text(s.inner_text())
            if value and len(value) < 50:
                skills.append(value)
        job["skills"] = skills
        job["skills_count"] = len(skills)
        # METADATA
        job["source"] = "rozee.pk"
        job["scraped_at"] = datetime.utcnow().isoformat()

        return job