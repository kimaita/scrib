import json
import os
from typing import Dict, Optional

from google.cloud import tasks_v2


def create_http_task(
    json_payload: Dict,
    url: Optional[str] = None,
    task_id: Optional[str] = None,
) -> tasks_v2.Task:
    """Create an HTTP POST task with a JSON payload.
    Args:
        url: The target URL of the task.
        json_payload: The JSON payload to send.
        task_id: ID to use for the newly created task.
    Returns:
        The newly created task.
    """

    client = tasks_v2.CloudTasksClient()

    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=url or f"https://{os.getenv('CLOUD_RUN_URL')}/episodes",
            headers={"Content-type": "application/json"},
            body=json.dumps(json_payload).encode(),
        ),
        name=(
            client.task_path(
                os.getenv("GCP_PROJECT_ID"),
                os.getenv("QUEUE_LOCATION_ID"),
                os.getenv("QUEUE_ID"),
                task_id,
            )
            if task_id is not None
            else None
        ),
    )

    response = client.create_task(
        tasks_v2.CreateTaskRequest(
            parent=client.queue_path(
                os.getenv("GCP_PROJECT_ID"),
                os.getenv("QUEUE_LOCATION_ID"),
                os.getenv("QUEUE_ID"),
            ),
            task=task,
        )
    )

    return response
