from abc import abstractmethod, ABC
from playwright.sync_api import sync_playwright
import json
from typing import List,Dict,Any,Union
from utils import handle_errors
from .roles import one_role
from src.utils.logger import get_logger

# LOGGER
logger = get_logger(__name__)

class Extractor(ABC):
    def __init__(self, base_url:str,card:str):
        self.base_url = base_url
        self.card = card
        self.role = one_role

    @abstractmethod
    def extract(self, card):
        pass

    @handle_errors
    def fetch_jobs(self, max_pages:int = 1) -> Union[bool,List[Any]]:
        jobs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            for page_num_1,page_num_0 in zip(range(1,max_pages+1),range(0,max_pages+1)):
                if self.base_url=="https://www.careerjet.com.pk/jobs?l=Pakistan&nw=1&s=":
                    url = self.base_url+self.role if page_num_1 == 1 else f"{self.base_url}{self.role}&p{page_num_1}"
                elif self.base_url=="https://www.rozee.pk/job/jsearch/q/":
                    url = self.base_url+self.role if page_num_0 == 0 else f"{self.base_url}{self.role}/stype/title/fpn/{page_num_0*20}"
                page.goto(url, timeout=60000)
                job_cards = page.query_selector_all(f"{self.card}")
                for card in job_cards:
                    job = self.extract(card)
                    if job and job.get("title"):
                        jobs.append(job)
        return jobs

    @staticmethod
    def clean_text(text:str) -> str:
        return " ".join(text.split()).strip(" ,.-") if text else ""

    @staticmethod
    @handle_errors
    def save_jobs(filename: str, jobs: List[Dict]):
        logger.info("Saving jobs...")
        with open(filename, "w") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        return True