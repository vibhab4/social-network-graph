# (: Connected :) — Social Network
### CS157C Team Project | Neo4j + Python

A console-based social networking app backed by Neo4j. Users can register, follow each other, get friend recommendations, and explore the network — all powered by graph traversal queries on the Stanford SNAP Facebook dataset.

---

## Project Structure

```
social-network-graph/
├── main.py                       # Console app entry point (all 11 use cases)
├── load_dataset.py               # One-time dataset loader
├── convert_edges.py              # Converts facebook_combined.txt to CSV format
├── facebook_combined.txt         # Raw SNAP edge list (undirected)
├── facebook_edges.csv            # Converted edge list (columns: user1, user2)
├── SocialMediaUsersDataset.csv   # Kaggle dataset (user attributes)
├── requirements.txt
├── README.md
├── .env.example                  # Credential template — copy to .env and fill in
├── db/
│   ├── __init__.py
│   └── neo4j_connection.py       # Neo4j driver (reads credentials from .env)
├── services/
│   ├── __init__.py
│   └── user_service.py           # All Cypher queries for every use case
└── templates/
    ├── base.html
    ├── circles.html
    ├── feed.html
    ├── profile.html
    └── search.html
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
URI      = "neo4j+s://YOUR_INSTANCE_ID.databases.neo4j.io"
USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"
```

For Neo4j Desktop (local), use:
```python
URI = "bolt://localhost:7687"
```

## Loading Dataset

1. Download `facebook_combined.txt.gz` from:
   https://snap.stanford.edu/data/ego-Facebook.html
2. Unzip it to get `facebook_combined.txt`.
3. Run this conversion script to generate `facebook_edges.csv`
   ```bash
   python convert_edges.py
   ```
4. Download `SocialMediaUsersDataset.csv` from:
   https://www.kaggle.com/datasets/arindamsahoo/social-media-users
5. Place it directly in the project root folder
6. Run:
```bash
python load_dataset.py
```

`facebook_combined.txt.gz` loads **4,039 users** and **176,468 directed FOLLOWS relationships** from the ego-Facebook dataset. Each undirected friendship edge is stored as two directed relationships so following/follower counts work correctly. Only needs to be run once.

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