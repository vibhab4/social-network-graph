from flask import Flask
from routes.users import users_bp
from routes.circles import circles_bp
from routes.recommendations import recommendations_bp

app = Flask(__name__)

app.register_blueprint(users_bp)
app.register_blueprint(circles_bp)
app.register_blueprint(recommendations_bp)

if __name__ == "__main__":
    app.run(debug=True)
    