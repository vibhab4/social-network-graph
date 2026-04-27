from flask import Blueprint, render_template
from db.neo4j_connection import get_driver

circles_bp = Blueprint('circles', __name__)

@circles_bp.route('/circles')
def circles():
    driver = get_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User)
            WITH u
            MATCH (u)-[:FRIEND]-(f:User)
            WITH u.id AS ego, 
                 count(DISTINCT f) AS member_count
            RETURN ego, member_count
            ORDER BY member_count DESC
            LIMIT 20
        """)
        circles = [{'ego': r['ego'], 
                    'member_count': r['member_count'],
                    'edge_count': r['member_count']} 
                   for r in result]
    return render_template('circles.html', circles=circles)