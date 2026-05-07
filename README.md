# (: Connected :) — Social Network
### CS157C Team Project | Neo4j + Python

A console-based social networking app backed by Neo4j. Users can register, follow each other, get friend recommendations, and explore the network — all powered by graph traversal queries on the Stanford SNAP Facebook dataset.

---

## Project Structure

```
social-network/
├── main.py                   # Console app entry point (all 11 use cases)
├── load_dataset.py           # One-time dataset loader (SNAP Facebook)
├── requirements.txt
├── README.md
├── .env                      # Your credentials (never committed)
├── db/
│   ├── __init__.py
│   └── neo4j_connection.py   # Neo4j driver (reads from .env)
└── services/
    ├── __init__.py
    └── user_service.py       # All Cypher queries for every use case
```

---

## Setup

### 1. Install dependencies

Clone the repo:
```bash
git clone https://github.com/vibhab4/social-network-graph.git
cd social-network-graph
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configure Neo4j

Edit `db/neo4j_connection.py` and fill in:
```python
URI      = "neo4j+s://YOUR_AURA_URI.databases.neo4j.io"
USERNAME = "YOUR_AURA_ID"
PASSWORD = "YOUR_PASSWORD"
```

For Neo4j Desktop (local), use:
```python
URI = "bolt://localhost:7687"
```

## Loading Dataset

1. Download `facebook_combined.txt.gz` from:
   https://snap.stanford.edu/data/ego-Facebook.html
2. Unzip it into the project root folder
3. Run:
```bash
python load_dataset.py
```

This loads **4,039 users** and **176,468 directed FOLLOWS relationships** from the ego-Facebook dataset. Each undirected friendship edge is stored as two directed relationships so following/follower counts work correctly. Only needs to be run once.

### 4. Run the app

```bash
python main.py
```

---

## Use Cases

 UC | Description 
-----------------
 UC-1 --> User Registration 
 UC-2 --> User Login 
 UC-3 --> View Profile 
 UC-4 --> Edit Profile 
 UC-5 --> Follow a User 
 UC-6 --> Unfollow a User 
 UC-7 --> View Following & Followers 
 UC-8 --> Mutual Connections 
 UC-9 --> Friend Recommendations 
 UC-10 --> Search Users 
 UC-11 --> Explore Popular Users 

## Project Structure


social-network/
├── main.py               #Console app entry point (all 11 UCs)
├── load_dataset.py       #One-time dataset loader
├── requirements.txt
├── README.md
├── db/
│   ├── __init__.py
│   └── neo4j_connection.py   #Neo4j driver config
└── services/
    ├── __init__.py
    └── user_service.py       #All Cypher queries

