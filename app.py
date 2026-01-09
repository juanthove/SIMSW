from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from dotenv import load_dotenv
load_dotenv()

from analysis.analysis_routes import analysis_bp
from auth.auth_routes import auth_bp

# registrar blueprints
app.register_blueprint(analysis_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)