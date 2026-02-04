from functools import wraps
from time import sleep
import logging

logger = logging.getLogger(__name__)


def handle_errors(max_retries=3, retry_delay=2, critical=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.warning(f"Retry {attempt}/{max_retries} for {func.__name__}")
                        sleep(retry_delay * (2 ** (attempt - 1)))  # Exponential backoff

                    return func(*args, **kwargs)

                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    if attempt == max_retries:
                        logger.error(f"Max retries reached for {func.__name__}: {e}")
                        if critical:
                            raise
                    continue

                except Exception as e:
                    logger.exception(f"Error in {func.__name__}: {e}")
                    last_error = e
                    break

            if critical and last_error:
                raise last_error
            return None

        return wrapper

    return decorator