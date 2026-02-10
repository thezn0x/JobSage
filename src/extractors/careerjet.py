from datetime import datetime
from src.utils.error_handler import handle_errors
from .base import Extractor
from src.utils.logger import get_logger
from typing import Dict,Any,Union

# LOGGER
logger = get_logger(__name__)

class CareerjetExtractor(Extractor):
    @handle_errors()
    def extract(self,card) -> Union[bool,Dict[str,Any]]:
        job={}
        def get_text(selector:str):
            element = card.query_selector(selector)
            return element.inner_text().strip() if element else "N/A"
        # GET TITLE
        title = get_text("header h2 a")
        job["title"]= title
        # GET APPLICATION URL
        appli_url = f"https://careerjet.com.pk{card.get_attribute('data-url')}"
        job["url"] = appli_url if appli_url else None
        # GET COMPANY NAME
        company = get_text("p a")
        job["company"]=company
        # GET LOCATION
        location = get_text("ul.location li")
        job["location"]=location + ", Pakistan"
        # GET DESCRIPTION
        description = get_text("div.desc")
        text = description
        job["description"]=description
        job["is_truncated"]=text.strip().endswith("…")
        # GET DATE
        date = get_text("footer ul.tags li span[class='badge badge-r badge-s badge-icon']")
        job["posted_date"]=date
        # EMPTY FIELDS
        job["experience_text"] = ""
        job["experience_years"] = None
        job["skills"] = []
        job["skills_count"] = None
        # METADATA
        job["source"] = "careerjet.pk"
        job["scraped_at"]=datetime.utcnow().isoformat()
        return job