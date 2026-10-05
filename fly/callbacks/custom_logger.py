"""
Proxy-level observability callback — the production-equivalent of notebook
Part 9 (per-call logging via litellm.success_callback / failure_callback),
but running here on the deployed proxy itself for every request, logged to
stdout so it shows up in `docker compose logs`, `fly logs`, or Render's log
stream without needing an external observability account.
"""
import logging

from litellm.integrations.custom_logger import CustomLogger

logger = logging.getLogger("liveramp-router")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class LiveRampUsageLogger(CustomLogger):
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            latency = (end_time - start_time).total_seconds()
            usage = getattr(response_obj, "usage", None)
            logger.info(
                "SUCCESS model=%s routed_to=%s cost=$%.6f latency=%.2fs input_tokens=%s output_tokens=%s user=%s",
                kwargs.get("model"),
                getattr(response_obj, "model", "unknown"),
                kwargs.get("response_cost") or 0.0,
                latency,
                getattr(usage, "prompt_tokens", "?"),
                getattr(usage, "completion_tokens", "?"),
                kwargs.get("user", "anonymous"),
            )
        except Exception as e:  # never let logging break a request
            logger.warning("logging error (success): %s", e)

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        try:
            logger.error(
                "FAILURE model=%s error=%s user=%s",
                kwargs.get("model"),
                kwargs.get("exception"),
                kwargs.get("user", "anonymous"),
            )
        except Exception as e:
            logger.warning("logging error (failure): %s", e)


proxy_handler_instance = LiveRampUsageLogger()
