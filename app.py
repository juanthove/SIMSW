from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from dotenv import load_dotenv
load_dotenv()

from analysis.analysis_routes import analysis_bp
from auth.auth_routes import auth_bp

#Importar endpoints
from database.routes.sitioWeb_routes import sitioWeb_bp 
from database.routes.analisis_routes import analisis_bp_db


# registrar blueprints
app.register_blueprint(analysis_bp)
app.register_blueprint(auth_bp)

#Blueprint de cada route con endpoints a la base de datos
app.register_blueprint(sitioWeb_bp)
app.register_blueprint(analisis_bp_db)

#Rutas a cada pagina
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/sites-create")
def sites_create():
    return render_template("site-create.html")

@app.route("/analysis-create")
def analysis_create():
    return render_template("analysis-create.html")

if __name__ == "__main__":
    app.run(debug=True)