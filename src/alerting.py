from uuid import UUID
from typing import Optional
import asyncio


from engrate_sdk.http.client import AsyncClient
from engrate_sdk.utils import log

logger = log.get_logger(__name__)

##TODO this should be moved to the SDK


async def send_to_slack(body: dict):
    """Sends a message to the Slack webhook."""
    # async with http_client.AsyncClient() as client:
    async with AsyncClient():
        # body =
        {
            "text": f"{body['message'] if body['message'] else 'Alert'}",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"uid: {body['uid']}"},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": body["exception"]},
                },
            ],
        }

        # headers =
        {"Content-type": "application/json"}
        # await client.post(env.get_slack_webhook_url(), json=body, headers=headers)


async def remove_throttled_alert(alert: str):
    """Removes a throttled alert from the set of triggered alerts."""
    await asyncio.sleep(1000)
    from api import app

    app.state.triggered_alerts.remove(alert)
    logger.info(f"Alert removed: {alert}")


# TODO: use oauth and proper API and update messages in-place with a counter
async def alert(
    uid: UUID, exception: Optional[Exception] = None, message: Optional[str] = None
):
    """Pings developers about an uncaught exception, with optional message."""
    alert = message or str(exception) or str(uid)
    from api import app

    if not hasattr(app.state, "triggered_alerts"):
        app.state.triggered_alerts = set()
    if alert not in app.state.triggered_alerts:
        app.state.triggered_alerts.add(alert)
        await send_to_slack(
            {"uid": str(uid), "message": message, "exception": str(exception)}
        )
        asyncio.create_task(remove_throttled_alert(alert))
