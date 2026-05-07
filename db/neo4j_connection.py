from neo4j import GraphDatabase

### NEO4J CREDENTIALS 
URI      = "neo4j+s://bc26e35f.databases.neo4j.io"
USERNAME = "bc26e35f"
PASSWORD = " "
####

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    return _driver

def close_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None

def run_query(query, parameters=None):
    driver = get_driver()
    with driver.session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]
