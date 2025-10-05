users_db = []

def signup_user(user):
    users_db.append(user)
    return user

def authenticate_user(user):
    for u in users_db:
        if u.email == user.email:
            return u
    return {"error": "User not found"}
