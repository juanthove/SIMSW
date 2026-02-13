from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

from dotenv import load_dotenv
load_dotenv()

from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.analisis_automatico import ejecutar_analisis_automaticos
from datetime import datetime, timezone


from analysis.analysis_routes import analysis_bp
from auth.auth_routes import auth_bp

#Importar endpoints
from database.routes.sitioWeb_routes import sitioWeb_bp 
from database.routes.analisis_routes import analisis_bp_db
from database.routes.informe_routes import informe_bp
from database.routes.detalleOZ_routes import detalleOZ_bp
from database.routes.mail_routes import mail_bp


# registrar blueprints
app.register_blueprint(analysis_bp)
app.register_blueprint(auth_bp)

#Blueprint de cada route con endpoints a la base de datos
app.register_blueprint(sitioWeb_bp)
app.register_blueprint(analisis_bp_db)
app.register_blueprint(informe_bp)
app.register_blueprint(detalleOZ_bp)
app.register_blueprint(mail_bp)

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

@app.route("/site-list")
def site_list():
    return render_template("site-list.html")

@app.route("/analysis-list")
def analysis_list():
    return render_template("analysis-list.html")

@app.route("/report-list")
def report_list():
    return render_template("report-list.html")

@app.route("/report-detail")
def report_detail():
    return render_template("report-detail.html")

@app.route("/site-history")
def site_history():
    return render_template("site-history.html")

@app.route("/mail-create")
def mail_create():
    return render_template("mail-create.html")


#Configurar ruta base
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOADS_DIR, exist_ok=True)

app.config["UPLOADS_DIR"] = UPLOADS_DIR


#Analisis automatico cada 15 minutos
scheduler = BackgroundScheduler()
scheduler.add_job(func=ejecutar_analisis_automaticos, trigger="interval", minutes=15, next_run_time=datetime.now(timezone.utc), args=[app], max_instances=1, coalesce=True, misfire_grace_time=500)

scheduler.start()
#if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#    scheduler.start()


if __name__ == "__main__":
    app.run(debug=True)