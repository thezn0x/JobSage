from pathlib import Path
import os
from config.settings import TRANSFORMERS
from src.loaders.main_loader import Loader
from config.settings import LOADERS
from typing import Dict,Any,Union
from src.utils.logger import get_logger

logger = get_logger(__name__)
DATA_MAP = {
    "rozee" : os.path.abspath(TRANSFORMERS["rozee"]["output_path"]),
    "careerjet" : os.path.abspath(TRANSFORMERS["careerjet"]["output_path"])
}

class PathError(Exception):
    pass

def filter_(data_map:Dict):
    new_map={}
    for k,v in data_map.items():
        if not isinstance(v,str):
            logger.warning(f"Skipping {k}: not a string (type: {type(v)})")
            continue
        if Path(v).exists():
            new_map[k] = v
            logger.debug(f"Included {k}: {v}")
        else:
            logger.warning(f"Skipping {k}: path does not exist - {v}")
        if not new_map:
            logger.error("No valid file paths found in data_map")
    return new_map

def main() -> Union[Dict[str,Any],None]:
    logger.info("Starting Loader...")
    try:
        loader = Loader(__name__)
        data = loader.get_data(filter_(DATA_MAP))
        logger.info("Loading skills to the database...")
        skill_keys = loader.load_skills("skills",data)
        logger.info("Loading locations to the database...")
        location_keys = loader.load_locations("locations",data)
        logger.info("Loading companies to the database...")
        company_keys = loader.load_companies("companies",data)
        logger.info("Loading platforms to the database...")
        platform_keys = loader.load_platforms("platforms",LOADERS)
        logger.info("Loading jobs to the database...")
        job_keys = loader.load_jobs("jobs",data,company_keys)
        logger.info("Loading junction tables...")
        job_skills_keys = loader.load_job_skills("job_skills",data,job_keys,skill_keys)
        job_location_keys = loader.load_job_locations("job_locations",data,job_keys, location_keys)
        job_platform_keys = loader.load_job_platforms("job_platforms",data,job_keys, platform_keys)
        keys = {
            'skill_keys' : skill_keys,
            'location_keys' : location_keys,
            'company_keys' : company_keys,
            'platform_keys' : platform_keys,
            'job_keys' : job_keys,
            'job_skills_keys' : job_skills_keys,
            'job_location_keys' : job_location_keys,
            'job_platform_keys' : job_platform_keys
        }
        logger.info("Loading complete! Loaded all data successfully.")
        return keys
    except Exception as e:
        logger.error("Error while performing %s: %s",__name__,e)
        return None

if __name__ == "__main__":
    main()