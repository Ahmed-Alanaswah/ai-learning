import re
import secrets
import time

ALERTS = {
    15: {
        "owner_id": "user-1",
        "name": "React Jobs",
        "time": "11:00",
        "timezone": "Asia/Amman",
        "version": 1,
    }
}

PENDING_ACTIONS = {}


def require_owned_alert(alert_id, user_id):
    alert = ALERTS.get(alert_id)

    if not alert or alert["owner_id"] != user_id:
        raise PermissionError("Alert not accessible")

    return alert


def validate_time(value):
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        raise ValueError("Invalid time format")


def request_update_alert(alert_id, new_time, user_id):
    # 1. Authorize and validate before creating a token
    alert = require_owned_alert(alert_id, user_id)
    validate_time(new_time)

    # 2. Store the intended change and current version
    token = secrets.token_urlsafe(24)

    PENDING_ACTIONS[token] = {
        "alert_id": alert_id,
        "user_id": user_id,
        "new_time": new_time,
        "expected_version": alert["version"],
        "expires_at": time.time() + 120,
    }

    return {
        "status": "confirmation_required",
        "old_time": alert["time"],
        "new_time": new_time,
        "confirmation_token": token,
    }


def confirm_update_alert(token, user_id):
    action = PENDING_ACTIONS.get(token)

    if not action or action["user_id"] != user_id:
        raise PermissionError("Invalid confirmation")

    if time.time() > action["expires_at"]:
        PENDING_ACTIONS.pop(token, None)
        raise ValueError("Confirmation expired")

    alert = require_owned_alert(action["alert_id"], user_id)

    # 3. Reject approval if alert changed since preview
    if alert["version"] != action["expected_version"]:
        PENDING_ACTIONS.pop(token, None)
        raise ValueError("409 Conflict: Alert was modified")

    # 4. Update only the requested field
    alert["time"] = action["new_time"]
    alert["version"] += 1

    # 5. Consume the confirmation
    del PENDING_ACTIONS[token]

    return {
        "status": "updated",
        "alert_id": action["alert_id"],
        "new_time": alert["time"],
    }


# TEST 1: Create a pending request
preview = request_update_alert(15, "12:00", "user-1")
token = preview["confirmation_token"]
print("Preview:", preview["status"])


# TEST 2: Another user cannot confirm it
try:
    confirm_update_alert(token, "user-2")
except PermissionError:
    print("Unauthorized confirmation blocked")


# TEST 3: User modifies the alert manually
ALERTS[15]["time"] = "13:00"
ALERTS[15]["version"] += 1

try:
    confirm_update_alert(token, "user-1")
except ValueError as error:
    print("Old confirmation rejected:", error)


# TEST 4: Create a new valid request
new_preview = request_update_alert(15, "16:00", "user-1")
new_token = new_preview["confirmation_token"]

result = confirm_update_alert(new_token, "user-1")
print("Update result:", result)


# TEST 5: Replay must fail
try:
    confirm_update_alert(new_token, "user-1")
except PermissionError:
    print("Replay blocked")


print("Final alert:", ALERTS[15])