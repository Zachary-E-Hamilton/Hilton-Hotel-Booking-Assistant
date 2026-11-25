import requests


class BookingAPIError(Exception):
    """A chat request failed with a message suitable for display."""

CHECK_RESERVATION = "For a booking or cancellation, check its status before resending."


def request_reply(endpoint: str, prompt: str, history: list[dict]) -> tuple[str, list[dict]]:
    payload = {"message": prompt, "history": history}

    try:
        res = requests.post(
            endpoint,
            json=payload,
            headers={"Accept": "application/json"},
            timeout=(5, 35),
            allow_redirects=False,
        )
    except requests.Timeout as exc:
        raise BookingAPIError(f"The booking service timed out. {CHECK_RESERVATION}") from exc
    except (
        requests.exceptions.InvalidURL,
        requests.exceptions.InvalidSchema,
        requests.exceptions.MissingSchema,
    ) as exc:
        raise BookingAPIError("The booking service URL is invalid. Check the full API Gateway endpoint.") from exc
    except requests.RequestException as exc:
        raise BookingAPIError(f"The booking service could not be reached. {CHECK_RESERVATION}") from exc

    status = res.status_code
    if status == 429:
        raise BookingAPIError("The booking service is busy. Wait a moment before sending another message.")
    if status == 504:
        raise BookingAPIError(f"The booking service timed out. {CHECK_RESERVATION}")
    if not 200 <= status < 300:
        raise BookingAPIError(f"The booking service returned HTTP {status}. {CHECK_RESERVATION}")

    try:
        data = res.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise BookingAPIError(f"The booking service returned unreadable JSON. {CHECK_RESERVATION}") from exc

    reply = data.get("reply") if isinstance(data, dict) else None
    if not isinstance(reply, str) or not reply.strip():
        raise BookingAPIError(f"The booking service returned no reply. {CHECK_RESERVATION}")

    next_history = data.get("history")
    if not isinstance(next_history, list):
        raise BookingAPIError(f"The booking service returned no conversation history. {CHECK_RESERVATION}")
    return reply.strip(), next_history
