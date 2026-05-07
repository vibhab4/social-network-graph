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

```bash
pip install -r requirements.txt
```

### 2. Configure Neo4j credentials

Create a `.env` file in the project root:

```
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-here
```

- **Neo4j Aura (cloud):** use `neo4j+s://` — URI and password are in the credentials `.txt` file downloaded when you created the instance. If you lost it, reset the password from [console.neo4j.io](https://console.neo4j.io).
- **Neo4j Desktop (local):** use `bolt://localhost:7687` with your local password.

> `.env` is in `.gitignore` and will never be committed.

### 3. Load the dataset

Download `facebook_combined.txt.gz` from the Stanford SNAP page:
https://snap.stanford.edu/data/ego-Facebook.html

Unzip it into the project root, then run:

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

All 11 use cases are accessible from the console menu after logging in.

| UC | Feature | Description |
|----|---------|-------------|
| UC-1 | User Registration | Sign up with name, email, username, and password. Password is hashed with SHA-256. Duplicate usernames are rejected. |
| UC-2 | User Login | Authenticate with username and password. |
| UC-3 | View Profile | See your name, email, bio, following count, and follower count. |
| UC-4 | Edit Profile | Update your display name and bio. |
| UC-5 | Follow a User | Create a directed FOLLOWS relationship to another user. |
| UC-6 | Unfollow a User | Remove a FOLLOWS relationship. |
| UC-7 | View Following / Followers | See two separate lists: who you follow and who follows you. |
| UC-8 | Mutual Connections | Enter another username to see users you both follow. |
| UC-9 | Friend Recommendations | Get suggestions based on 2-hop graph traversal (you → A → B, recommend B), ranked by number of shared connections. |
| UC-10 | Search Users | Case-insensitive partial search by name or username. |
| UC-11 | Explore Popular Users | See the top 10 most-followed users in the network. |

---

## Dataset

**ego-Facebook** — Stanford SNAP  
https://snap.stanford.edu/data/ego-Facebook.html

Anonymised social circles collected from Facebook. Each node is a user, each edge is a mutual friendship. The dataset covers 10 ego-networks from volunteer participants.

| Stat | Value |
|------|-------|
| Users (nodes) | 4,039 |
| Friendships (undirected edges) | 88,234 |
| FOLLOWS relationships loaded | 176,468 |

---

## Graph Schema

**Node:** `:User`  
Properties: `username`, `name`, `email`, `password`, `bio`, `created`, `node_id`

**Relationship:** `(:User)-[:FOLLOWS]->(:User)`  
No properties on the relationship itself.

**Indexes:** `user_username` (primary lookup), `user_node_id` (used during dataset load)