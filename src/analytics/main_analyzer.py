from typing import List, Dict, Any, Optional, Union
from src.utils.logger import get_logger
from config.settings import LOADERS
from dotenv import load_dotenv
from znpg import Database
import os

from utils import handle_errors

load_dotenv(LOADERS["dotenv_path"])
logger = get_logger(__name__)


class Analyzer:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not set in environment!")

    def get_result(self, query: str, params: Union[List, None] = None) -> List[Dict[str, Any]]:
        try:
            with Database() as db:
                db.url_connect(self.db_url)
                results = db.query(query, params)
            return results
        except ConnectionError:
            logger.exception('Critical error in %s', __name__)
            raise ConnectionError('Error while connecting to the database')

    @handle_errors
    def get_top_skills(self, limit: int = 10) -> List[Dict[str, Any]]:
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
        results = self.get_result(query, [limit])

        logger.info(f"Retrieved top {len(results)} skills")
        return results

    @handle_errors
    def get_skill_details(self, skill_name: str) -> Optional[Dict[str, Any]]:
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

    @handle_errors
    def get_skill_combinations(self, skill_name: str, limit: int = 5) -> List[Dict[str, Any]]:
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

        results = self.get_result(query, [skill_name, skill_name, limit])

        logger.info(f"Found {len(results)} skills that pair with {skill_name}")
        return results

    @handle_errors
    def get_jobs_by_location(self) -> List[Dict[str, Any]]:
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

    @handle_errors
    def get_top_skills_in_city(self, city: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            s.skill_name,
            COUNT(DISTINCT j.job_id) as job_count
        FROM locations l
        JOIN job_locations jl USING(location_id)
        JOIN jobs j ON jl.job_id = j.job_id
        JOIN job_skills js ON j.job_id = js.job_id
        JOIN skills s USING(skill_id)
        WHERE l.city = %s
        GROUP BY s.skill_id, s.skill_name
        ORDER BY job_count DESC
        LIMIT %s
        """
        results = self.get_result(query, [city, limit])
        logger.info(f"Retrieved top {len(results)} skills in {city}")
        return results

    @handle_errors
    def get_top_city_hiring(self) -> Dict[str, Any]:
        query = """
        SELECT 
            l.city,
            COUNT(*) as job_count
        FROM job_locations jl
        JOIN locations l ON jl.location_id = l.location_id
        GROUP BY jl.location_id, l.city
                """
        results = self.get_result(query)
        top_city = results[0]
        logger.info(f"Retrieved top city hiring: {len(results)}")
        return top_city

    @handle_errors
    def get_companies_in_city(self, city: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                c.name as company_name,
                COUNT(DISTINCT j.job_id) as job_count
            FROM locations l
            JOIN job_locations jl USING(location_id)
            JOIN jobs j ON jl.job_id = j.job_id
            JOIN companies c USING(company_id)
            WHERE l.city = %s
            GROUP BY c.company_id, c.name
            ORDER BY job_count DESC
            LIMIT %s"""
        results = self.get_result(query, [city, limit])
        logger.info(f"Retrieved {len(results)} companies in {city}")
        return results

    @handle_errors
    def get_top_hiring_companies(self, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
                SELECT c.name,
                       COUNT(j.job_id) as job_count,
                       ROUND( 
                               COUNT(j.job_id) * 100.0 /
                               (SELECT COUNT(*) FROM jobs),
                               2
                       )               as percentage
                FROM companies c
                         JOIN jobs j USING (company_id)
                GROUP BY c.company_id, c.name
                ORDER BY job_count DESC
                    LIMIT %s
                """
        results = self.get_result(query, [limit])
        logger.info(f"Found {len(results)} companies")
        return results

    @handle_errors
    def get_company_skills(self, company_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
                SELECT s.skill_name,
                       COUNT(DISTINCT j.job_id) as job_count
                FROM companies c
                         JOIN jobs j USING (company_id)
                         JOIN job_skills js ON j.job_id = js.job_id
                         JOIN skills s USING (skill_id)
                WHERE c.name = %s
                GROUP BY s.skill_id, s.skill_name
                ORDER BY job_count DESC
                    LIMIT %s
                """
        results = self.get_result(query, [company_name, limit])
        logger.info(f"Found {len(results)} skills for {company_name}")
        return results

    @handle_errors
    def get_company_locations(self, company_name: str) -> List[Dict[str, Any]]:
        query = """
                SELECT l.city,
                       l.country,
                       COUNT(DISTINCT j.job_id) as job_count
                FROM companies c
                         JOIN jobs j USING (company_id)
                         JOIN job_locations jl ON j.job_id = jl.job_id
                         JOIN locations l ON jl.location_id = l.location_id
                WHERE c.name = %s
                GROUP BY l.location_id, l.city, l.country
                ORDER BY job_count DESC
                """
        results = self.get_result(query, [company_name])
        logger.info(f"Found {len(results)} locations for {company_name}")
        return results