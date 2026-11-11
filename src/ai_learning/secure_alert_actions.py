# Mock database
ALERTS = {
    15: {"owner_id": "user-1", "name": "React Jobs"},
    16: {"owner_id": "user-2", "name": "Java Jobs"},
}


def get_alert_for_user(
    alert_id: int,
    authenticated_user_id: str,
):
    alert = ALERTS.get(alert_id)

    if not alert or alert["owner_id"] != authenticated_user_id:
        raise PermissionError("Alert not found or not accessible")

    return alert


def preview_delete_alert(
    alert_id: int,
    authenticated_user_id: str,
):
    alert = get_alert_for_user(
        alert_id,
        authenticated_user_id,
    )

    return {
        "status": "confirmation_required",
        "alert_id": alert_id,
        "alert_name": alert["name"],
    }


def delete_alert_after_confirmation(
    alert_id: int,
    authenticated_user_id: str,
    confirmed: bool,
):
    if not confirmed:
        return {"status": "cancelled"}

    # Recheck ownership at execution time
    get_alert_for_user(alert_id, authenticated_user_id)

    del ALERTS[alert_id]

    return {"status": "deleted", "alert_id": alert_id}


# Simulated authenticated session
current_user_id = "user-1"

# print(preview_delete_alert(15, current_user_id))

# # Confirmation is simulated here, not obtained from AI
# print(
#     delete_alert_after_confirmation(
#         alert_id=15,
#         authenticated_user_id=current_user_id,
#         confirmed=True,
#     )
# )

print("Remaining alerts:", ALERTS)

def test_delete_preview(user_id: str, alert_id: int):
    try:
        result = preview_delete_alert(alert_id, user_id)
        print("Success:", result)

    except PermissionError as error:
        print("Access denied:", str(error))


# Test 1: Owner can access the alert
test_delete_preview("user-1", 15)

# Test 2: Another user cannot access it
test_delete_preview("user-2", 15)

# Test 3: User 2 can access their own alert
test_delete_preview("user-2", 16)