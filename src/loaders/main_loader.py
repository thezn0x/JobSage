from src.utils.logger import get_logger
from config.settings import DATABASE_URL
from typing import List, Dict, Any, Union
from znpg import Database
import json

logger = get_logger(__name__)
class Loader:
    def __init__(self,name:str):
        self.name = name

    @staticmethod
    def get_unique(data:List[Dict[str,Any]],field:str) -> Union[None,List[Any]]:
        try:
            non_unique = []
            for one in data:
                non_unique.append(one.get(field,None))
            if isinstance(non_unique[0],list):
                unique_data = []
                for one in non_unique:
                    unique_data.extend(one)
            else:
                unique_data = list(set(non_unique))
            return unique_data
        except Exception as e:
            logger.exception("Critical error while performing %s: %s",__name__,e)

    @staticmethod
    def load_get_keys(table:str, to_load:List[Dict[str,Any]], columns:List[str]) -> Union[None,List[Dict[str,Any]]]:
        try:
            with Database() as db:
                db.url_connect(DATABASE_URL)
                db.bulk_insert(table,to_load,"DO NOTHING")
                keys = db.select(table, columns)
            return keys
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    @staticmethod
    def get_data(data_map:Dict[str,Any]) -> Union[None,List[Dict[str,Any]]]:
        try:
            data = []
            for name,path in data_map.items():
                with open(path,"r") as f:
                    _data = json.load(f)
                    data.extend(_data)
            return data
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    def load_companies(self,table:str , data: List[Dict[str,Any]]) -> Union[List[Dict[str,Any]],None]:
        try:
            companies = self.get_unique(data,"company")
            loading_list = []
            for company in companies:
                if company != "N/A":
                    loading_list.append({"name":company})
            return self.load_get_keys(table,loading_list,["company_id","name"])
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    def load_skills(self,table:str ,data:List[Dict[str,Any]]) -> Union[List[Dict[str,Any]],None]:
        try:
            placeholder_skills = self.get_unique(data,"core_skills")
            skills = list(set(placeholder_skills))
            to_load = []
            for skill in skills:
                to_load.append({"skill_name":skill})
            return self.load_get_keys(table,to_load,["skill_id","skill_name"])
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    def load_platforms(self, table: str, platforms_config: Dict[str, Any]) -> Union[None,List[Dict[str, Any]]]:
        try:
            all_platforms = []
            platforms = platforms_config.get("platforms", platforms_config)
            for platform_name, platform_data in platforms.items():
                if isinstance(platform_data, dict):
                    platform_data["platform_name"] = platform_name
                    all_platforms.append(platform_data)
            return self.load_get_keys(table,all_platforms,["platform_id", "platform_name"])
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    def load_locations(self, table:str, data:List[Dict[str,Any]]) -> Union[None,List[Dict[str, Any]]]:
        try:
            locations = self.get_unique(data, "location")
            location_list = []
            for location in locations:
                string_parts = location.split(",")
                if len(string_parts) > 1:
                    location_list.append({"city": string_parts[0].strip(), "country": string_parts[1].strip()})
                else:
                    location_list.append({"city":string_parts[0].strip(),"country":"Pakistan"})
            return self.load_get_keys(table,location_list,["location_id","city","country"])
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    def load_jobs(self, table:str, data:List[Dict[str,Any]], company_keys:List[Dict[str,Any]]) -> Union[None,List[Dict[str, Any]]]:
        try:
            jobs_list = []
            company_map = {c["name"]: c["company_id"] for c in company_keys}
            for job in data:
                if job["company"] not in company_map:
                    continue
                job_data = {
                    "title": job["title"],
                    "company_id": company_map[job["company"]],
                    "description": job.get("description"),
                    "application_url": job.get("application_url"),
                    "min_salary": job.get("min_salary"),
                    "max_salary": job.get("max_salary"),
                    "posted_date": job.get("posted_date"),
                    "min_experience": job.get("min_experience"),
                    "salary_currency": "PKR",
                    "scraped_date": job.get("scraped_date")
                }
                jobs_list.append(job_data)
            return self.load_get_keys(table,jobs_list,['job_id',"title","application_url"])
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    def junction_abstraction(self,table:str, data:List[Dict[str,Any]], job_keys:List[Dict[str,Any]], entity_keys:List[Dict[str,Any]], job_field:str, entity_field:str, entity_name:str) -> Union[None,List[Dict[str,Any]]]:
        try:
            job_lookup = {job["application_url"]: job["job_id"] for job in job_keys}
            entity_lookup = {entity[entity_field]: entity[entity_name] for entity in entity_keys}
            junc_list = []
            for job in data:
                if job.get('application_url') not in job_lookup:
                    continue
                job_id = job_lookup[job.get('application_url')]
                values = job.get(job_field)
                if not values:
                    continue
                if not isinstance(values,list):
                    values = [values]
                for value in values:
                    if value not in entity_lookup:
                        continue
                    entity_id = entity_lookup[value]
                    junc_list.append({'job_id':job_id, entity_name:entity_id})
            return self.load_get_keys(table, junc_list, ["job_id", entity_name])
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    def load_job_skills(self, table:str, data:List[Dict[str,Any]], job_keys:List[Dict[str,Any]], skill_keys:List[Dict[str,Any]]) -> Union[None,List[Dict[str,Any]]]:
        try:
            return self.junction_abstraction(
                table, data, job_keys, skill_keys,
                job_field="core_skills",
                entity_field="skill_name",
                entity_name="skill_id"
            )
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    def load_job_locations(self, table:str, data:List[Dict[str,Any]],job_keys:List[Dict[str,Any]], location_keys:List[Dict[str,Any]]) -> Union[None,List[Dict[str,Any]]]:
        try:
            job_lookup = {job["application_url"]:job["job_id"] for job in job_keys}
            location_lookup = {(location["city"],location["country"]):location["location_id"] for location in location_keys}
            jun_list = []
            for job in data:
                job_id = job_lookup[job["application_url"]]
                location_str = job.get('location')
                parts = location_str.split(",")
                city = parts[0].strip()
                country = parts[1] if len(parts)>1 else "Pakistan"
                loc = (city, country)
                if loc in location_lookup:
                    loc_id = location_lookup[loc]
                    jun_list.append({'job_id':job_id,'location_id':loc_id})
            return self.load_get_keys(table,jun_list,["job_id","location_id"])
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)

    def load_job_platforms(self, table:str, data:List[Dict[str,Any]], job_keys:List[Dict[str,Any]], platform_keys:List[Dict[str,Any]]) -> Union[None,List[Dict[str,Any]]]:
        try:
            return self.junction_abstraction(
                table, data, job_keys, platform_keys,
                job_field="source",
                entity_field="platform_name",
                entity_name="platform_id"
            )
        except Exception as e:
            logger.exception("Critical error while performing %s: %s", __name__,e)