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



# """
# load_dataset.py

# """

# import os
# import random
# from db.neo4j_connection import run_query, _driver
# from dotenv import load_dotenv
# import pandas as pd
# import hashlib
# import ast
# from faker import Faker
# from neo4j import GraphDatabase

# load_dotenv()

# NEO4J_URI      = os.getenv("NEO4J_URI")
# NEO4J_USER     = os.getenv("NEO4J_USER")
# NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# # Replace with your own file path
# USERS_CSV      = "/Users/aravpanchmatia/social_network_graph/SocialMediaUsersDataset.csv"

# # Replace with your own file path
# EDGES_CSV      = "/Users/aravpanchmatia/social_network_graph/facebook_edges.csv"   # columns: user1, user2  

# # How many users to load (facebook_ed has ~4039 unique nodes)
# MAX_USERS = 4039

# # HELPERS
# fake = Faker()
# random.seed(42)

# used_usernames = set()

# def make_username(name: str) -> str:
#     """Generate a unique username from a real name."""
#     parts = name.lower().split()
#     base  = f"{parts[0]}_{parts[-1]}" if len(parts) > 1 else parts[0]
#     # remove non-alphanumeric except underscore
#     base  = "".join(c for c in base if c.isalnum() or c == "_")
#     username = base
#     # keep adding a number suffix until unique
#     while username in used_usernames:
#         username = f"{base}{random.randint(1, 999)}"
#     used_usernames.add(username)
#     return username

# def make_email(username: str) -> str:
#     domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"]
#     return f"{username}@{random.choice(domains)}"

# def hash_password(plain: str) -> str:
#     return hashlib.sha256(plain.encode()).hexdigest()

# def make_password() -> str:
#     """Return (plain_text, hashed) — plain is never stored in Neo4j."""
#     plain = f"Pass{random.randint(1000,9999)}!"
#     return hash_password(plain)

# def parse_interests(raw: str) -> list:
#     """Parse interest string like \"'Movies', 'Gaming'\" into a list."""
#     try:
#         return [i.strip() for i in ast.literal_eval(f"[{raw}]")]
#     except Exception:
#         return []


# # LOAD & PREPARE DATA
# print("Loading CSV files...")

# users_df = pd.read_csv(USERS_CSV, nrows=MAX_USERS)
# edges_df = pd.read_csv(EDGES_CSV)

# print(f"{len(users_df)} users loaded")
# print(f"{len(edges_df)} friendship edges loaded")

# # Build enriched user records
# print("\n Generating usernames, emails, passwords...")
# user_records = []
# for _, row in users_df.iterrows():
#     username = make_username(str(row["Name"]))
#     email    = make_email(username)
#     pwd_hash = make_password()

#     interests = parse_interests(str(row["Interests"])) if pd.notna(row["Interests"]) else []
#     # deduplicate interests per user
#     interests = list(dict.fromkeys(interests))

#     user_records.append({
#         "userId"  : int(row["UserID"]),
#         "name"    : str(row["Name"]),
#         "username": username,
#         "email"   : email,
#         "password": pwd_hash,
#         "gender"  : str(row["Gender"]),
#         "dob"     : str(row["DOB"]),
#         "city"    : str(row["City"]),
#         "country" : str(row["Country"]),
#         "interests": interests,
#     })

# print(f"Done — {len(user_records)} user records ready")

# # Valid user IDs for filtering edges
# valid_ids = {r["userId"] for r in user_records}
# edges = [
#     (int(r["user1"]), int(r["user2"]))
#     for _, r in edges_df.iterrows()
#     if int(r["user1"]) in valid_ids and int(r["user2"]) in valid_ids
# ]
# print(f"{len(edges)} edges within valid user range")


# # NEO4J LOADER
# class Neo4jLoader:
#     def __init__(self, driver):
#         self.driver = driver
#         print("\nConnected to Neo4j")

#     def close(self):
#         self.driver.close()

#     def run(self, query, params=None):
#         with self.driver.session() as session:
#             session.run(query, params or {})

#     def clear_database(self):
#         print("\n️Clearing existing data...")
#         self.run("MATCH (n) DETACH DELETE n")
#         print("Database cleared")

#     def create_constraints(self):
#         print("\nCreating constraints & indexes...")
#         constraints = [
#             "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User)     REQUIRE u.userId   IS UNIQUE",
#             "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User)     REQUIRE u.username IS UNIQUE",
#             "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User)     REQUIRE u.email    IS UNIQUE",
#             "CREATE CONSTRAINT IF NOT EXISTS FOR (c:City)     REQUIRE c.name     IS UNIQUE",
#             "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Interest) REQUIRE i.name     IS UNIQUE",
#         ]
#         for c in constraints:
#             self.run(c)
#         print("Constraints created")

#     def load_users(self, records, batch_size=500):
#         print(f"\nLoading {len(records)} User nodes...")
#         for i in range(0, len(records), batch_size):
#             batch = records[i:i + batch_size]
#             self.run("""
#                 UNWIND $batch AS u
#                 MERGE (user:User {userId: u.userId})
#                 SET user.name     = u.name,
#                     user.username = u.username,
#                     user.email    = u.email,
#                     user.password = u.password,
#                     user.gender   = u.gender,
#                     user.dob      = u.dob
#             """, {"batch": batch})
#             print(f"Users {i+1}–{min(i+batch_size, len(records))} loaded")

#     def load_cities(self, records, batch_size=500):
#         print(f"\nLoading City nodes & LIVES_IN relationships...")
#         for i in range(0, len(records), batch_size):
#             batch = records[i:i + batch_size]
#             self.run("""
#                 UNWIND $batch AS u
#                 MERGE (c:City {name: u.city})
#                 SET c.country = u.country
#                 WITH c, u
#                 MATCH (user:User {userId: u.userId})
#                 MERGE (user)-[:LIVES_IN]->(c)
#             """, {"batch": batch})
#             print(f"Cities {i+1}–{min(i+batch_size, len(records))} loaded")

#     def load_interests(self, records, batch_size=500):
#         print(f"\nLoading Interest nodes & INTERESTED_IN relationships...")
#         # Flatten to (userId, interest) pairs
#         pairs = [
#             {"userId": r["userId"], "interest": interest}
#             for r in records
#             for interest in r["interests"]
#         ]
#         for i in range(0, len(pairs), batch_size):
#             batch = pairs[i:i + batch_size]
#             self.run("""
#                 UNWIND $batch AS p
#                 MERGE (i:Interest {name: p.interest})
#                 WITH i, p
#                 MATCH (user:User {userId: p.userId})
#                 MERGE (user)-[:INTERESTED_IN]->(i)
#             """, {"batch": batch})
#         print(f"{len(pairs)} interest relationships loaded")

#     def load_follows(self, edges, batch_size=1000):
#         print(f"\n🔗 Loading {len(edges)} FOLLOWS relationships...")
#         edge_dicts = [{"u1": e[0], "u2": e[1]} for e in edges]
#         for i in range(0, len(edge_dicts), batch_size):
#             batch = edge_dicts[i:i + batch_size]
#             self.run("""
#                 UNWIND $batch AS e
#                 MATCH (a:User {userId: e.u1})
#                 MATCH (b:User {userId: e.u2})
#                 MERGE (a)-[:FOLLOWS]->(b)
#             """, {"batch": batch})
#             print(f"Edges {i+1}–{min(i+batch_size, len(edge_dicts))} loaded")
    
#     def print_summary(self):
#         print("\nDatabase Summary:")
#         with self.driver.session() as session:
#             counts = {
#                 "User nodes"          : "MATCH (u:User)         RETURN count(u) AS c",
#                 "City nodes"          : "MATCH (c:City)         RETURN count(c) AS c",
#                 "Interest nodes"      : "MATCH (i:Interest)     RETURN count(i) AS c",
#                 "FOLLOWS edges"       : "MATCH ()-[r:FOLLOWS]->()     RETURN count(r) AS c",
#                 "LIVES_IN edges"      : "MATCH ()-[r:LIVES_IN]->()    RETURN count(r) AS c",
#                 "INTERESTED_IN edges" : "MATCH ()-[r:INTERESTED_IN]->() RETURN count(r) AS c",
#             }
#             for label, query in counts.items():
#                 result = session.run(query).single()
#                 print(f"   {label}: {result['c']:,}")


# # MAIN
# if __name__ == "__main__":
#     loader = Neo4jLoader(driver)

#     try:
#         loader.clear_database()
#         loader.create_constraints()
#         loader.load_users(user_records)
#         loader.load_cities(user_records)
#         loader.load_interests(user_records)
#         loader.load_follows(edges)
#         loader.print_summary()

#     except Exception as e:
#         print(f"\nError: {e}")
#         raise

#     finally:
#         loader.close()
