"""
load_dataset.py

"""

import os
import random
from db.neo4j_connection import run_query, close_driver

EDGE_FILE = "facebook_combined.txt"

FIRST_NAMES = ["Alex","Jordan","Morgan","Taylor","Casey","Riley","Quinn",
               "Drew","Avery","Blake","Charlie","Dana","Emerson","Finley",
               "Harley","Jamie","Kendall","Logan","Mackenzie","Noel"]
LAST_NAMES  = ["Smith","Johnson","Lee","Brown","Garcia","Wilson","Martinez",
               "Anderson","Thomas","Jackson","White","Harris","Martin",
               "Thompson","Moore","Young","Allen","King","Wright","Scott"]

def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_email(uid):
    domains = ["gmail.com","yahoo.com","outlook.com","sjsu.edu","hotmail.com"]
    return f"user_{uid}@{random.choice(domains)}"

def load():
    if not os.path.exists(EDGE_FILE):
        print(f" '{EDGE_FILE}' not found.")
        print("    Download from: https://snap.stanford.edu/data/ego-Facebook.html")
        return

    print("Reading edge list...")
    edges = []
    node_ids = set()
    with open(EDGE_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            a, b = line.split()
            edges.append((int(a), int(b)))
            node_ids.update([int(a), int(b)])

    print(f"   Found {len(node_ids)} unique nodes and {len(edges)} edges.")

    ### Creat constraint & indexes 
    print("Creating constraint...")
    run_query("CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE")

    ### Batch-create User nodes 
    print(" Creating User nodes...")
    BATCH = 500
    node_list = [
        {"uid": uid,
         "username": f"user_{uid}",
         "name": random_name(),
         "email": random_email(uid),
         "bio": "",
         "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"}  # "password"
        for uid in node_ids
    ]
    for i in range(0, len(node_list), BATCH):
        batch = node_list[i:i+BATCH]
        run_query("""
            UNWIND $batch AS row
            MERGE (u:User {username: row.username})
            ON CREATE SET u.name     = row.name,
                          u.email    = row.email,
                          u.bio      = row.bio,
                          u.password = row.password,
                          u.created  = timestamp()
        """, {"batch": batch})
        print(f"   Nodes: {min(i+BATCH, len(node_list))}/{len(node_list)}", end="\r")
    print()

    ### Batch-create FOLLOWS relationships 
    print(" Creating FOLLOWS relationships (bidirectional)...")
    rel_batch = [{"a": f"user_{a}", "b": f"user_{b}"} for a, b in edges]
    for i in range(0, len(rel_batch), BATCH):
        batch = rel_batch[i:i+BATCH]
        run_query("""
            UNWIND $batch AS row
            MATCH (a:User {username: row.a}), (b:User {username: row.b})
            MERGE (a)-[:FOLLOWS]->(b)
            MERGE (b)-[:FOLLOWS]->(a)
        """, {"batch": batch})
        print(f"   Relationships: {min(i+BATCH, len(rel_batch))}/{len(rel_batch)}", end="\r")
    print()

    print(" Dataset loaded successfully!")
    close_driver()

if __name__ == "__main__":
    load()
