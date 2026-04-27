from flask import Blueprint, render_template, request
from db.neo4j_connection import get_driver

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@users_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: toInteger($id)})
                OPTIONAL MATCH (u)-[:FRIEND]-(f)
                RETURN u.id AS id, count(f) AS friend_count
            """, id=query)
            for record in result:
                results.append({
                    'id': record['id'],
                    'friend_count': record['friend_count']
                })
    return render_template('search.html', results=results, query=query)


@users_bp.route('/profile/<int:user_id>')
def profile(user_id):
    driver = get_driver()
    with driver.session() as session:
        # Get friends
        friends_result = session.run("""
            MATCH (u:User {id: $id})-[:FRIEND]-(f:User)
            RETURN f.id AS id
            ORDER BY f.id
        """, id=user_id)
        friends = [{'id': r['id']} for r in friends_result]

        # Get recommendations (friends of friends)
        rec_result = session.run("""
            MATCH (u:User {id: $id})-[:FRIEND]-(f:User)-[:FRIEND]-(rec:User)
            WHERE rec.id <> $id
            AND NOT (u)-[:FRIEND]-(rec)
            RETURN rec.id AS id, count(f) AS mutual
            ORDER BY mutual DESC
            LIMIT 10
        """, id=user_id)
        recommendations = [{'id': r['id'], 'mutual': r['mutual']} for r in rec_result]

        # Get circles count
        circles_result = session.run("""
            MATCH (u:User {id: $id})-[:FRIEND]-(f:User)
            RETURN count(f) AS circle_count
        """, id=user_id)
        circles = [r for r in circles_result]

    return render_template('profile.html',
        user_id=user_id,
        friends=friends,
        recommendations=recommendations,
        circles=circles
    )