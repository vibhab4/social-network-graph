# Social Network – CS157C Team Project

## Setup

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
2. Unzip it to get `facebook_combined.txt`
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
This loads ~4,039 users and ~176,000 follow relationships.

## Run the App

```bash
python main.py
```

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
├── SocialMediaUsersDataset.csv
├── facebook_edges.csv
├── .env
├── .env.example
├── requirements.txt
├── .gitignore
├── README.md
├── db/
│   ├── __init__.py
│   └── neo4j_connection.py   #Neo4j driver config
└── services/
    ├── __init__.py
    └── user_service.py       #All Cypher queries

