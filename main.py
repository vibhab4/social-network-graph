"""
main.py - Social Network Console App
CS157C Team Project
"""
from db.neo4j_connection import close_driver
from services.user_service import (
    register_user, login_user, view_profile, edit_profile,
    follow_user, unfollow_user, view_following, view_followers,
    mutual_connections, friend_recommendations, search_users, popular_users
)


def divider(title=""):
    print("\n--- " + title + " ---" if title else "\n" + "-" * 40)

def pause():
    input("-⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻--⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻-")
    input("\nPress Enter to continue")
    input("-⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻--⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻-")


def main_menu():
    print("\n      (: Connected :) - Network")
    print("-⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻--⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻-")
    print("- 1. Register")
    print("- 2. Login")
    print("- 0. Exit")
    print("-⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻--⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻-")
    return input("Enter choice: ").strip()


def user_menu(username):
    print("\n-⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻--⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻-")
    print("Hello " + username + "Welcome to the network")
    print("-⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻--⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻-")
    print("- 1.  View Profile")
    print("- 2.  Edit Profile")
    print("- 3.  Follow a User")
    print("- 4.  Unfollow a User")
    print("- 5.  View Following / Followers")
    print("- 6.  Connections")
    print("- 7.  Friend Recommendations")
    print("- 8.  Search Users")
    print("- 9.  Explore Popular Users")
    print("- 0.  Logout")
    print("-⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻--⎽__⎽-⎻⎺⎺⎻-⎽__⎽--⎻⎺⎺⎻-")
    return input("Enter choice: ").strip()


# UC-1: Register
def handle_register():
    divider("_⎽-⎻⎺⎺⎻-⎽__Register User_⎽-⎻⎺⎺⎻-⎽__")
    name     = input("Full name: ").strip()
    email    = input("Email: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if not all([name, email, username, password]):
        print("Error, All fields are required.")
        pause()
        return

    result = register_user(name, email, username, password)
    if result.get("exists"):
        print("Username '" + username + "' is already taken.")
    else:
        print("Account created. Welcome, " + name + ".")
    pause()


# UC-2: Login
def handle_login():
    divider("_⎽-⎻⎺⎺⎻-⎽__Login")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    user = login_user(username, password)
    if user:
        print("Login successful. Welcome back " + user["name"] + ".")
        return user["username"]
    else:
        print("Invalid username or password.")
        pause()
        return None


# View Profile
def handle_view_profile(username):
    divider("_⎽-⎻⎺⎺⎻-⎽__View Profiles")
    p = view_profile(username)
    if p:
        print("Username  : " + str(p["username"]))
        print("Name      : " + str(p["name"]))
        print("Email     : " + str(p["email"]))
        print("Bio       : " + (p["bio"] if p["bio"] else "(no bio)"))
        print("Following : " + str(p["following_count"]))
        print("Followers : " + str(p["follower_count"]))
    else:
        print("Profile not found.")
    pause()


# UC-4: Edit Profile
def handle_edit_profile(username):
    divider("_⎽-⎻⎺⎺⎻-⎽__Edit Profile")
    p = view_profile(username)
    if not p:
        print("Profile not found.")
        pause()
        return

    print("Current name: " + str(p["name"]))
    new_name = input("New name (press Enter to keep): ").strip()
    if not new_name:
        new_name = p["name"]

    print("Current bio: " + (p["bio"] if p["bio"] else "(empty)"))
    new_bio = input("New bio (press Enter to keep): ").strip()
    if not new_bio:
        new_bio = p["bio"] or ""

    ok = edit_profile(username, new_name, new_bio)
    print("Profile updated." if ok else "Update failed.")
    pause()


# UC-5: Follow a User
def handle_follow(username):
    divider("_⎽-⎻⎺⎺⎻-⎽__Follow a User")
    target = input("Enter username to follow: ").strip()
    status = follow_user(username, target)
    if status == "ok":
        print("You are now following " + target + ".")
    elif status == "cannot_self_follow":
        print("You cannot follow yourself.")
    else:
        print("User " + target + " not found.")
    pause()


# UC-6: Unfollow a User
def handle_unfollow(username):
    divider("_⎽-⎻⎺⎺⎻-⎽__Unfollow a User")
    target = input("Enter username to unfollow: ").strip()
    unfollow_user(username, target)
    print("You have unfollowed " + target + ".")
    pause()


# UC-7: View Following and Followers
def handle_connections(username):
    divider("_⎽-⎻⎺⎺⎻-⎽__Following and Followers")

    following = view_following(username)
    print("\nPeople you follow (" + str(len(following)) + "):")
    for u in following:
        print("  " + u["username"] + " - " + u["name"])
    if not following:
        print("  (none)")

    followers = view_followers(username)
    print("\nYour followers (" + str(len(followers)) + "):")
    for u in followers:
        print("  " + u["username"] + " - " + u["name"])
    if not followers:
        print("  (none)")
    pause()


# UC-8: Mutual Connections
def handle_mutual(username):
    divider("_⎽-⎻⎺⎺⎻-⎽__Connections")
    other = input("Enter username to compare with: ").strip()
    mutuals = mutual_connections(username, other)
    print("\nConnections with " + other + " (" + str(len(mutuals)) + "):")
    for u in mutuals:
        print("  " + u["username"] + " - " + u["name"])
    if not mutuals:
        print("  (none)")
    pause()


# UC-9: Friend Recommendations
def handle_recommendations(username):
    divider("_⎽-⎻⎺⎺⎻-⎽__Friend Recommendations")
    recs = friend_recommendations(username)
    print("\nSuggested users to follow:")
    for r in recs:
        print("  " + r["username"] + " - " + r["name"] + " (" + str(r["common_connections"]) + " mutual connections)")
    if not recs:
        print("  No recommendations yet. Try following more users.")
    pause()


# UC-10: Search Users
def handle_search():
    divider("_⎽-⎻⎺⎺⎻-⎽__Search Users")
    query = input("Search by name or username: ").strip()
    results = search_users(query)
    print("\nResults for '" + query + "' (" + str(len(results)) + "):")
    for u in results:
        print("  " + u["username"] + " - " + u["name"])
    if not results:
        print("  No users found.")
    pause()


# UC-11: Popular Users
def handle_popular():
    divider("_⎽-⎻⎺⎺⎻-⎽__Popular Users")
    users = popular_users()
    print("\nMost followed users:")
    for i, u in enumerate(users, 1):
        print("  " + str(i) + ". " + u["username"] + " - " + u["name"] + " (" + str(u["follower_count"]) + " followers)")
    if not users:
        print("  No data available.")
    pause()


# Main app loop
def run():
    current_user = None
    try:
        while True:
            if current_user is None:
                choice = main_menu()
                if choice == "1":
                    handle_register()
                elif choice == "2":
                    current_user = handle_login()
                elif choice == "0":
                    print("Goodbye.")
                    break
                else:
                    print("Invalid option. Try again.")
            else:
                choice = user_menu(current_user)
                if   choice == "1": handle_view_profile(current_user)
                elif choice == "2": handle_edit_profile(current_user)
                elif choice == "3": handle_follow(current_user)
                elif choice == "4": handle_unfollow(current_user)
                elif choice == "5": handle_connections(current_user)
                elif choice == "6": handle_mutual(current_user)
                elif choice == "7": handle_recommendations(current_user)
                elif choice == "8": handle_search()
                elif choice == "9": handle_popular()
                elif choice == "0":
                    print("Logged out.")
                    current_user = None
                else:
                    print("Invalid option. Try again.")
    finally:
        close_driver()


if __name__ == "__main__":
    run()