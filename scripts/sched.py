import sys
import subprocess
import time
from datetime import datetime
from src.utils.logger import get_logger
from apscheduler.schedulers.blocking import BlockingScheduler
from config.settings import SCHEDULER

logger = get_logger(__name__)

def run_etl():
    start_time = datetime.now()
    try:
        result = subprocess.run(
            ['bash', 'run.sh'],
            capture_output=True,
            text=True,
            check=True,
            timeout=1800
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("ETL Pipeline completed successfully!")
        logger.info(f"Duration: {duration:.2f} seconds")

        if result.stdout:
            logger.info("Output:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
        return True

    except subprocess.TimeoutExpired:
        logger.error("ETL Pipeline timed out (> 30 minutes)")
        return False

    except subprocess.CalledProcessError as e:
        logger.error("ETL Pipeline failed!")
        logger.error(f"Exit code: {e.returncode}")

        if e.stderr:
            logger.error("Error output:")
            for line in e.stderr.split('\n'):
                if line.strip():
                    logger.error(f"  {line}")

        return False

    except FileNotFoundError:
        logger.error("run_etl.py not found!")
        logger.error("Make sure you're running from the correct directory")
        return False

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def main():
    logger.info("JobSage ETL Scheduler Starting...")
    logger.info(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Schedule: Daily at 2:00 AM")
    logger.info("")

    scheduler = BlockingScheduler()

    scheduler.add_job(
        run_etl,
        trigger='cron',
        hour=SCHEDULER['hour'],
        minute=SCHEDULER['minute'],
        id='daily_etl',
        name='Daily ETL Pipeline',
        replace_existing=True
    )

    logger.info("Running ETL immediately on startup...")
    run_etl()

    logger.info("")
    logger.info("Scheduler is now running. Press Ctrl+C to stop.")
    logger.info("")

    try:
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        logger.info("")
        logger.info("Scheduler stopped by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Scheduler crashed: {e}")
        time.sleep(60)
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)