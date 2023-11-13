def user_schema(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "email": user["email"],
        "disabled": user["disabled"],
        "password": user.get("password", ""),
    }


def users_schema(users) -> list:
    return [user_schema(user) for user in users]
