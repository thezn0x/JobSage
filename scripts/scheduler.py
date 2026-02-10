from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
from src.utils.logger import get_logger

logger = get_logger(__name__)

def run_etl():
    logger.info("Starting SkillScout ETL...")
    try:
        result = subprocess.run(
            ['python', 'run_etl.py'],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("ETL completed successfully!")
        logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"ETL failed: {e.stderr}")

scheduler = BlockingScheduler()

scheduler.add_job(run_etl, 'cron', hour=2, minute=0)

run_etl()

logger.info("Scheduler started. Next run at 2:00 AM daily.")

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    logger.info("Scheduler stopped.")