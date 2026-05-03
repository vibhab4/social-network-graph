"""
services/user_service.py
11 use cases.
"""
import hashlib
from db.neo4j_connection import run_query


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

