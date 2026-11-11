import secrets
import time

ALERTS = {
    15: {"owner_id": "user-1", "name": "React Jobs"},
    16: {"owner_id": "user-2", "name": "Java Jobs"},
}

PENDING_ACTIONS = {}


def require_owned_alert(alert_id, user_id):
    alert = ALERTS.get(alert_id)

    if alert is None or alert["owner_id"] != user_id:
        raise PermissionError("Alert not accessible")

    return alert


def request_delete_alert(alert_id, user_id):
    alert = require_owned_alert(alert_id, user_id)

    token = secrets.token_urlsafe(24)

    PENDING_ACTIONS[token] = {
        "alert_id": alert_id,
        "user_id": user_id,
        "expires_at": time.time() + 120,
    }

    return {
        "status": "confirmation_required",
        "alert_name": alert["name"],
        "confirmation_token": token,
    }


def confirm_delete_alert(token, user_id):
    action = PENDING_ACTIONS.get(token)

    if not action or action["user_id"] != user_id:
        raise PermissionError("Invalid confirmation")

    if time.time() > action["expires_at"]:
        del PENDING_ACTIONS[token]
        raise ValueError("Confirmation expired")

    alert_id = action["alert_id"]

    # Authorization is checked again at execution time
    require_owned_alert(alert_id, user_id)

    del ALERTS[alert_id]
    del PENDING_ACTIONS[token]

    return {"status": "deleted", "alert_id": alert_id}


# Simulated authenticated user
current_user = "user-1"

preview = request_delete_alert(15, current_user)
print("Preview:", preview["status"], preview["alert_name"])

token = preview["confirmation_token"]

# Another user attempts to confirm the deletion
try:
    confirm_delete_alert(token, "user-2")
except PermissionError:
    print("Unauthorized confirmation blocked")

# The original user confirms the deletion
result = confirm_delete_alert(token, current_user)
print("Result:", result)

# Reusing the same confirmation must fail
try:
    confirm_delete_alert(token, current_user)
except PermissionError:
    print("Replay blocked")

print("Remaining alerts:", ALERTS)