"""
services/user_service.py
11 use cases.
"""
import hashlib
from db.neo4j_connection import run_query


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# UC-1: User Registration
def register_user(name: str, email: str, username: str, password: str) -> dict:
    hash = hash_password(password)
    result = run_query("""
        MERGE (u:User {username: $username})
        ON CREATE SET u.name = $name,
                      u.email = $email,
                      u.password = $password,
                      u.bio = '',
                      u.created = timestamp(),
                      u.already_exists = false
        ON MATCH SET  u.already_exists = true
        RETURN u.username AS username, u.already_exists AS exists
    """, {"username": username, "name": name, "email": email, "password": hash})
    return result[0] if result else {}

# UC-2: User Login
def user_login(username: str, password: str) -> dict | None:
    hash = hash_password(password)
    result = run_query("""
        MATCH (u:User {username: $username, password: $password})
        RETURN u.username AS username, u.name AS name, u.email AS email, u.bio AS bio
    """, {"username": username, "password": hash})
    return result[0] if result else None

# UC-3: View Profile
def view_profile(username: str) -> dict | None:
    result = run_query("""
        MATCH (u:User {username: $username})
        OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
        OPTIONAL MATCH (follower)-[:FOLLOWS]->(u)
        RETURN u.username AS username,
               u.name AS name,
               u.email AS email,
               u.bio AS bio,
               count(DISTINCT following) AS following_count,
               count(DISTINCT follower) AS follower_count
    """, {"username": username})
    return result[0] if result else None

# UC-4: Edit Profile
def edit_profile(username: str, new_name: str, new_bio: str) -> bool:
    result = run_query("""
        MATCH (u:User {username: $username})
        SET u.name = $name,
            u.bio = $bio
        RETURN u.username AS username
    """, {"username": username, "name": new_name, "bio": new_bio})
    return len(result) > 0

# UC-5: Follow User
def follow_user(follower_username: str, target_username: str) -> str:
    if follower_username == target_username:
        return "cannot_self_follow"
    result = run_query("""
        MATCH (u1:User {username: $follower}), (u2:User {username: $target})
        MERGE (u1)-[r:FOLLOWS]->(u2)
        RETURN type(r) AS relation
    """, {"follower": follower_username, "target": target_username}) 
    return "ok" if result else "User not found"

# UC-6: Unfollow User
def unfollow_user(follower_username: str, target_username: str) -> bool:
    result = run_query("""
        MATCH (u1:User {username: $follower})-[r:FOLLOWS]->(u2:User {username: $target})
        DELETE r
        RETURN count(r) AS deleted
    """, {"follower": follower_username, "target": target_username})
    return True

# UC-7: View Following
def view_following(username):
    return run_query("""
        MATCH (u:User {username: $username})-[:FOLLOWS]->(f:User)
        RETURN f.username AS username, f.name AS name
        ORDER BY f.name
    """, {"username": username})

# UC-7: View Followers
def view_followers(username):
    return run_query("""
        MATCH (f:User)-[:FOLLOWS]->(u:User {username: $username})
        RETURN f.username AS username, f.name AS name
        ORDER BY f.name
    """, {"username": username})

# UC-8: Mutual Connections
def mutual_connections(username, other_username):
    return run_query("""
        MATCH (u:User {username: $username})-[:FOLLOWS]->(mutual:User)
              <-[:FOLLOWS]-(other:User {username: $other})
        RETURN mutual.username AS username, mutual.name AS name
        ORDER BY mutual.name
    """, {"username": username, "other": other_username})

# UC-9: Friend Recommendations
def friend_recommendations(username, limit=10):
    return run_query("""
        MATCH (u:User {username: $username})-[:FOLLOWS]->(middle:User)
                                            -[:FOLLOWS]->(rec:User)
        WHERE rec.username <> $username
          AND NOT (u)-[:FOLLOWS]->(rec)
        RETURN rec.username AS username,
               rec.name AS name,
               count(middle) AS common_connections
        ORDER BY common_connections DESC
        LIMIT $limit
    """, {"username": username, "limit": limit})


# UC-10: Search Users
def search_users(query):
    return run_query("""
        MATCH (u:User)
        WHERE toLower(u.username) CONTAINS $pattern
           OR toLower(u.name) CONTAINS $pattern
        RETURN u.username AS username, u.name AS name
        ORDER BY u.username
        LIMIT 25
    """, {"pattern": query.lower()})


# UC-11: Popular Users
def popular_users(limit=10):
    return run_query("""
        MATCH (u:User)
        OPTIONAL MATCH (follower:User)-[:FOLLOWS]->(u)
        RETURN u.username AS username,
               u.name AS name,
               count(follower) AS follower_count
        ORDER BY follower_count DESC
        LIMIT $limit
    """, {"limit": limit})