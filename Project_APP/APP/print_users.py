from db import get_all_users

if __name__ == "__main__":
    users = get_all_users()
    print("Users in database:")
    for u in users:
        print(f"ID: {getattr(u, 'id', None)}, Username: {getattr(u, 'username', None)}")