from flask import Blueprint, render_template, request
from db.neo4j_connection import get_driver

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/feed')
def feed():
    user_id = request.args.get('user_id', '').strip()
    recommendations = []
    if user_id:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: toInteger($id)})-[:FRIEND]-(f:User)-[:FRIEND]-(rec:User)
                WHERE rec.id <> toInteger($id)
                AND NOT (u)-[:FRIEND]-(rec)
                RETURN rec.id AS id, count(f) AS mutual
                ORDER BY mutual DESC
                LIMIT 15
            """, id=user_id)
            recommendations = [{'id': r['id'], 'mutual': r['mutual']} for r in result]
    return render_template('feed.html', 
                           recommendations=recommendations, 
                           user_id=user_id)