from fastapi.middleware.cors import CORSMiddleware
from src.analytics.main_analyzer import Analyzer
from typing import Any, Dict, Callable
from fastapi import FastAPI, HTTPException
from src.utils.logger import get_logger
from datetime import datetime
from functools import wraps

app = FastAPI(
    title="SkillScout API",
    description="Job market analytics API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = Analyzer()
logger = get_logger(__name__)

def handle_errors(func: Callable) -> Callable:
    """Decorator to handle common API errors and ensure consistent response format"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # Ensure result is never None for list responses
            if result is None:
                result = []
            return {
                "success": True,
                "data": result
            }
        except ConnectionError as e:
            logger.error(f'Database connection error in {func.__name__}: {e}')
            raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
        except IndexError as e:
            logger.error(f'No data found in {func.__name__}: {e}')
            raise HTTPException(status_code=404, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f'Unexpected error in {func.__name__}: {e}')
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    return wrapper

@app.get('/')
def root():
    return {
        "service": "SkillScout API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat() + "Z",
        "documentation": "/docs",
        "endpoints": {
            "skills": [
                "GET /skills/trending",
                "GET /skills/trending/{city_name}",
                "GET /skills/detail/{skill_name}",
                "GET /skills/combinations/{skill_name}"
            ],
            "locations": [
                "GET /locations/jobs",
                "GET /locations/cities/top"
            ]
        }
    }

@app.get('/skills/trending')
@handle_errors
def get_trending_skills(limit: int = 10) -> Dict[str, Any]:
    skills = analyzer.get_top_skills(limit=limit) or []
    return {
        "count": len(skills),
        "top_skill": skills[0] if skills else None,
        "skills": skills
    }

@app.get('/skills/detail/{skill_name}')
@handle_errors
def get_skill_detail(skill_name: str) -> Dict[str, Any]:
    skill = analyzer.get_skill_details(skill_name)
    if not skill:
        raise IndexError(f"Skill '{skill_name}' not found")
    return {"skill": skill}

@app.get('/skills/combinations/{skill_name}')
@handle_errors
def get_skill_combinations(skill_name: str, limit: int = 5) -> Dict[str, Any]:
    combos = analyzer.get_skill_combinations(skill_name, limit) or []
    return {
        "skill": skill_name,
        "count": len(combos),
        "combinations": combos
    }

@app.get("/locations/jobs")
@handle_errors
def get_jobs_by_location() -> Dict[str, Any]:
    locations = analyzer.get_jobs_by_location() or []
    return {
        "count": len(locations),
        "locations": locations
    }

@app.get("/skills/trending/{city_name}")
@handle_errors
def get_trending_skills_by_city(city_name: str, limit: int = 10) -> Dict[str, Any]:
    skills = analyzer.get_top_skills_in_city(city_name, limit) or []
    return {
        "city": city_name,
        "count": len(skills),
        "skills": skills
    }

@app.get("/locations/cities/top")
@handle_errors
def get_top_hiring_cities() -> Dict[str, Any]:
    cities = analyzer.get_top_city_hiring() or []
    return {
        "count": len(cities),
        "cities": cities
    }

@app.get("/locations/{city_name}/companies")
@handle_errors
def companies(city_name: str, limit: int = 10) -> Dict[str, Any]:
    companies_list = analyzer.get_companies_in_city(city_name, limit) or []
    return {
        "count": len(companies_list),
        "companies": companies_list
    }

@app.get("/companies/top")
@handle_errors
def get_top_companies() -> Dict[str, Any]:
    companies_list = analyzer.get_top_hiring_companies() or []
    return {
        "count": len(companies_list),
        "companies": companies_list
    }

@app.get("/companies/{company_name}/skills")
@handle_errors
def company_skills(company_name: str, limit: int = 10) -> Dict[str, Any]:
    skills = analyzer.get_company_skills(company_name, limit) or []
    return {
        "count": len(skills),
        "skills": skills
    }

@app.get("/companies/locations/{company_name}")
@handle_errors
def company_locations(company_name: str) -> Dict[str, Any]:
    locations = analyzer.get_company_locations(company_name) or []
    return {
        "count": len(locations),
        "locations": locations
    }