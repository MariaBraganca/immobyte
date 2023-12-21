import openai
import logging

logger = logging.getLogger(__name__)

def log_openai_error(function):
    async def wrapper(*arg, **kwargs):
        try:
            return await function(*arg, **kwargs)
        except openai.APIConnectionError as e:
            logger.error("The server could not be reached")
            logger.error(e.__cause__)  # an underlying Exception, likely raised within httpx.
        except openai.RateLimitError:
            logger.error("A 429 status code was received; we should back off a bit.")
        except openai.APIStatusError as e:
            logger.error("Another non-200-range status code was received")
            logger.error(e.status_code)
            logger.error(e.response)
    return wrapper
