def user_schema(user) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "email": user["email"],
        "disabled": user["disabled"],
        "password": user.get("password", ""),
        "role": user.get("role", None),
    }


def users_schema(users) -> list:
    return [user_schema(user) for user in users]