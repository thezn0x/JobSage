from src.analytics.main_analyzer import Analyzer
from src.utils.logger import get_logger
from datetime import datetime
from fastapi import FastAPI, HTTPException

analyzer = Analyzer()
logger = get_logger(__name__)
app = FastAPI(
    title="SkillScout API",
    description="API for SkillScout analytics",
    version="1.0.0"
)

@app.get('/')
def root():
    return {
        "service": "SkillScout API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "documentation": "/docs",
        "endpoints": [
            "/skills/trending",
        ]
    }

@app.get(path='/skills/trending')
def analyze_skills(limit:int = 10):
    response = {"success": False, "error": None}
    try:
        skills = analyzer.get_top_skills(limit=limit)
        response['success'] = True
        response['top_skill'] = skills[0] if skills else None
        response['top_skills'] = skills
        return response
    except ConnectionError as e:
        logger.error('Check your connection and try again later: %s', e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except IndexError as e:
        logger.error('No skills found: %s', e)
        raise HTTPException(status_code=404, detail="No skills data available")
    except Exception as e:
        logger.exception('Critical internal error in %s: %s', __name__, e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get('/skills/detail/{skill_name}')
def skill_detail(skill_name:str):
    response = {"success": False, "error": None}
    try:
        skill = analyzer.get_skill_details(skill_name)
        response['success'] = True
        response['skill_detail'] = skill if skill else None
        return response
    except ConnectionError as e:
        logger.error('Check your connection and try again later: %s', e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.exception('Critical internal error in %s: %s', __name__, e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get('/skills/combinations/{skill_name}')
def skill_combinations(skill_name:str, limit:int = 5):
    response = {"success": False, "error": None}
    try:
        combos = analyzer.get_skill_combinations(skill_name, limit)
        response['success'] = True
        response['skill_combinations'] = combos
        return response
    except ConnectionError as e:
        logger.error('Check your connection and try again later: %s', e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except IndexError as e:
        logger.error('No skills found: %s', e)
        raise HTTPException(status_code=404, detail="No skills data available")
    except Exception as e:
        logger.exception('Critical internal error in %s: %s', __name__, e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/job/locations")
def job_locations():
    response = {"success": False, "error": None}
    try:
        value = analyzer.get_jobs_by_location()
        response['success'] = True
        response['jobs_by_locations'] = value
        return response
    except ConnectionError as e:
        logger.error('Check your connection and try again later: %s', e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except IndexError as e:
        logger.error('No skills found: %s', e)
        raise HTTPException(status_code=404, detail="No skills data available")
    except Exception as e:
        logger.exception('Critical internal error in %s: %s', __name__, e)
        raise HTTPException(status_code=500, detail="Internal server error")