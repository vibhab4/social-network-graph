"""
services/user_service.py
All Cypher queries for the 11 use cases.
"""
import hashlib
from db.neo4j_connection import run_query


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── UC-1: User Registration ───────────────────────────────────────────────────
def register_user(name: str, email: str, username: str, password: str) -> dict:
    """
    Cypher:
        MERGE (u:User {username: $username})
        ON CREATE SET u.name=$name, u.email=$email,
                      u.password=$password, u.bio='', u.created=timestamp()
        ON MATCH SET  u.already_exists = true
        RETURN u
    """
    hashed = hash_password(password)
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
    """, {"username": username, "name": name,
          "email": email, "password": hashed})
    return result[0] if result else {}


# ── UC-2: User Login ──────────────────────────────────────────────────────────
def login_user(username: str, password: str) -> dict | None:
    """
    Cypher:
        MATCH (u:User {username: $username, password: $password})
        RETURN u
    """
    hashed = hash_password(password)
    result = run_query("""
        MATCH (u:User {username: $username, password: $password})
        RETURN u.username AS username, u.name AS name, u.email AS email, u.bio AS bio
    """, {"username": username, "password": hashed})
    return result[0] if result else None


# ── UC-3: View Profile ────────────────────────────────────────────────────────
def view_profile(username: str) -> dict | None:
    """
    Cypher:
        MATCH (u:User {username: $username})
        OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
        OPTIONAL MATCH (follower)-[:FOLLOWS]->(u)
        RETURN u, count(DISTINCT following) AS following_count,
               count(DISTINCT follower) AS follower_count
    """
    result = run_query("""
        MATCH (u:User {username: $username})
        OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
        OPTIONAL MATCH (follower)-[:FOLLOWS]->(u)
        RETURN u.username AS username,
               u.name     AS name,
               u.email    AS email,
               u.bio      AS bio,
               count(DISTINCT following) AS following_count,
               count(DISTINCT follower)  AS follower_count
    """, {"username": username})
    return result[0] if result else None


# ── UC-4: Edit Profile ────────────────────────────────────────────────────────
def edit_profile(username: str, new_name: str, new_bio: str) -> bool:
    """
    Cypher:
        MATCH (u:User {username: $username})
        SET u.name = $name, u.bio = $bio
        RETURN u
    """
    result = run_query("""
        MATCH (u:User {username: $username})
        SET u.name = $name, u.bio = $bio
        RETURN u.username AS username
    """, {"username": username, "name": new_name, "bio": new_bio})
    return len(result) > 0


# ── UC-5: Follow User ─────────────────────────────────────────────────────────
def follow_user(follower_username: str, target_username: str) -> str:
    """
    Cypher:
        MATCH (a:User {username: $follower}), (b:User {username: $target})
        MERGE (a)-[r:FOLLOWS]->(b)
        RETURN type(r) AS rel
    """
    if follower_username == target_username:
        return "cannot_self_follow"
    result = run_query("""
        MATCH (a:User {username: $follower}), (b:User {username: $target})
        MERGE (a)-[r:FOLLOWS]->(b)
        RETURN type(r) AS rel
    """, {"follower": follower_username, "target": target_username})
    return "ok" if result else "user_not_found"


# ── UC-6: Unfollow User ───────────────────────────────────────────────────────
def unfollow_user(follower_username: str, target_username: str) -> bool:
    """
    Cypher:
        MATCH (a:User {username: $follower})-[r:FOLLOWS]->(b:User {username: $target})
        DELETE r
    """
    result = run_query("""
        MATCH (a:User {username: $follower})-[r:FOLLOWS]->(b:User {username: $target})
        DELETE r
        RETURN count(r) AS deleted
    """, {"follower": follower_username, "target": target_username})
    return True


# ── UC-7: View Connections (Following / Followers) ────────────────────────────
def view_following(username: str) -> list:
    """
    Cypher:
        MATCH (u:User {username: $username})-[:FOLLOWS]->(f)
        RETURN f.username, f.name
    """
    return run_query("""
        MATCH (u:User {username: $username})-[:FOLLOWS]->(f)
        RETURN f.username AS username, f.name AS name
        ORDER BY f.name
    """, {"username": username})


def view_followers(username: str) -> list:
    """
    Cypher:
        MATCH (f)-[:FOLLOWS]->(u:User {username: $username})
        RETURN f.username, f.name
    """
    return run_query("""
        MATCH (f)-[:FOLLOWS]->(u:User {username: $username})
        RETURN f.username AS username, f.name AS name
        ORDER BY f.name
    """, {"username": username})


# ── UC-8: Mutual Connections ──────────────────────────────────────────────────
def mutual_connections(username: str, other_username: str) -> list:
    """
    Cypher:
        MATCH (u:User {username: $username})-[:FOLLOWS]->(mutual)
              <-[:FOLLOWS]-(o:User {username: $other})
        RETURN mutual.username, mutual.name
    """
    return run_query("""
        MATCH (u:User {username: $username})-[:FOLLOWS]->(mutual)
              <-[:FOLLOWS]-(o:User {username: $other})
        RETURN mutual.username AS username, mutual.name AS name
        ORDER BY mutual.name
    """, {"username": username, "other": other_username})


# ── UC-9: Friend Recommendations ──────────────────────────────────────────────
def friend_recommendations(username: str, limit: int = 5) -> list:
    """
    Cypher:
        MATCH (u:User {username: $username})-[:FOLLOWS]->(a)-[:FOLLOWS]->(rec)
        WHERE rec <> u AND NOT (u)-[:FOLLOWS]->(rec)
        RETURN rec.username, rec.name, count(a) AS common_connections
        ORDER BY common_connections DESC LIMIT $limit
    """
    return run_query("""
        MATCH (u:User {username: $username})-[:FOLLOWS]->(a)-[:FOLLOWS]->(rec)
        WHERE rec <> u AND NOT (u)-[:FOLLOWS]->(rec)
        RETURN rec.username AS username,
               rec.name     AS name,
               count(a)     AS common_connections
        ORDER BY common_connections DESC
        LIMIT $limit
    """, {"username": username, "limit": limit})


# ── UC-10: Search Users ───────────────────────────────────────────────────────
def search_users(query: str) -> list:
    """
    Cypher:
        MATCH (u:User)
        WHERE toLower(u.name) CONTAINS toLower($q)
           OR toLower(u.username) CONTAINS toLower($q)
        RETURN u.username, u.name
        LIMIT 10
    """
    return run_query("""
        MATCH (u:User)
        WHERE toLower(u.name)     CONTAINS toLower($q)
           OR toLower(u.username) CONTAINS toLower($q)
        RETURN u.username AS username, u.name AS name
        ORDER BY u.name
        LIMIT 10
    """, {"q": query})


# ── UC-11: Explore Popular Users ──────────────────────────────────────────────
def popular_users(limit: int = 10) -> list:
    """
    Cypher:
        MATCH (u:User)<-[:FOLLOWS]-(f)
        RETURN u.username, u.name, count(f) AS follower_count
        ORDER BY follower_count DESC LIMIT $limit
    """
    return run_query("""
        MATCH (u:User)<-[:FOLLOWS]-(f)
        RETURN u.username AS username,
               u.name     AS name,
               count(f)   AS follower_count
        ORDER BY follower_count DESC
        LIMIT $limit
    """, {"limit": limit})
