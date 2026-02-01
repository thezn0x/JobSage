from typing import List, Dict, Any, Optional, Union
from src.utils.logger import get_logger
from config.settings import LOADERS
from dotenv import load_dotenv
from znpg import Database
import os

load_dotenv(LOADERS["dotenv_path"])
logger = get_logger(__name__)


class  Analyzer:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not set in environment!")

    def get_result(self, query:str, params:Union[List,None]=None) -> List[Dict[str, Any]]:
        try:
            with Database() as db:
                db.url_connect(self.db_url)
                results = db.query(query, params)
            return results
        except ConnectionError:
            logger.exception('Critical error in %s',__name__)
            raise ConnectionError('Error while connecting to the database')

    def get_top_skills(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            query = """
                SELECT 
                    s.skill_name,
                    COUNT(DISTINCT js.job_id) as job_count,
                    ROUND(
                        COUNT(DISTINCT js.job_id) * 100.0 / 
                        (SELECT COUNT(*) FROM jobs),
                        2
                    ) as percentage
                FROM skills s
                JOIN job_skills js USING(skill_id)
                GROUP BY s.skill_id, s.skill_name
                ORDER BY job_count DESC
                LIMIT %s
            """

            # Execute query
            results = self.get_result(query,[limit])

            logger.info(f"Retrieved top {len(results)} skills")
            return results

        except Exception as e:
            logger.exception(f"Error getting top skills: {e}")
            return []

    def get_skill_details(self, skill_name: str) -> Optional[Dict[str, Any]]:
        try:
            query = """
                SELECT 
                    s.skill_name,
                    COUNT(DISTINCT js.job_id) as job_count,
                    ROUND(
                        COUNT(DISTINCT js.job_id) * 100.0 / 
                        (SELECT COUNT(*) FROM jobs),
                        2
                    ) as percentage
                FROM skills s
                JOIN job_skills js USING(skill_id)
                WHERE s.skill_name = %s
                GROUP BY s.skill_id, s.skill_name
            """

            results = self.get_result(query, [skill_name])

            if results:
                return results[0]
            else:
                logger.warning(f"Skill not found: {skill_name}")
                return None

        except Exception as e:
            logger.exception(f"Error getting skill details: {e}")
            return None

    def get_skill_combinations(self, skill_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            query = """
                WITH target_jobs AS (
                    SELECT js.job_id
                    FROM job_skills js
                    JOIN skills s USING(skill_id)
                    WHERE s.skill_name = %s
                )
                SELECT 
                    s.skill_name,
                    COUNT(*) as co_occurrence_count,
                    ROUND(
                        COUNT(*) * 100.0 / 
                        (SELECT COUNT(*) FROM target_jobs),
                        2
                    ) as percentage_with_target
                FROM target_jobs tj
                JOIN job_skills js ON tj.job_id = js.job_id
                JOIN skills s USING(skill_id)
                WHERE s.skill_name != %s
                GROUP BY s.skill_id, s.skill_name
                ORDER BY co_occurrence_count DESC
                LIMIT %s
            """

            results = self.get_result(query,[skill_name, skill_name, limit])

            logger.info(f"Found {len(results)} skills that pair with {skill_name}")
            return results

        except Exception as e:
            logger.exception(f"Error getting skill combinations: {e}")
            return []

    def get_jobs_by_location(self):
        try:
            query = """
                    SELECT l.location_id, l.city, l.country,
                      COUNT(DISTINCT jl.job_id) as job_count
                    FROM locations l
                    LEFT JOIN job_locations jl ON l.location_id = jl.location_id
                    GROUP BY l.location_id, l.city, l.country
                    ORDER BY job_count DESC
            """
            results = self.get_result(query)
            logger.info(f"Retrieved {len(results)} jobs by location")
            return results
        except Exception as e:
            logger.exception(f"Error getting jobs and locations: {e}")
            return []

# testing
if __name__ == "__main__":
    analyzer = Analyzer()
    resp = analyzer.get_jobs_by_location()
    print(resp)