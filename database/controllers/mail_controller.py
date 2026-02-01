from sqlalchemy.exc import IntegrityError
from database.connection import SessionLocal
from database.models.mail_model import Mail
from database.models.sitioMail_model import SitioMail
from database.models.sitioWeb_model import SitioWeb


# -----------------------------
# OBTENER MAILS
# -----------------------------
def obtener_mails():
    db = SessionLocal()
    try:
        mails = db.query(Mail).all()
        resultado = []

        for m in mails:
            sitios = db.query(SitioMail.sitio_web_id).filter(
                SitioMail.mail_id == m.id
            ).all()

            resultado.append({
                "id": m.id,
                "nombre": m.nombre,
                "email": m.correo,
                "sitios": [s[0] for s in sitios]
            })

        return resultado
    finally:
        db.close()


# -----------------------------
# CREAR MAIL
# -----------------------------
def crear_mail(data):
    db = SessionLocal()
    try:
        mail = Mail(
            nombre=data.get("nombre"),
            correo=data.get("email")
        )
        db.add(mail)
        db.commit()
        db.refresh(mail)

        sitios = data.get("sitios")

        # 👉 TODOS los sitios
        if sitios is None:
            sitios_db = db.query(SitioWeb.id).all()
            sitios = [s[0] for s in sitios_db]

        for sitio_id in sitios:
            db.add(SitioMail(
                sitio_web_id=sitio_id,
                mail_id=mail.id
            ))

        db.commit()

        return {
            "id": mail.id,
            "nombre": mail.nombre,
            "email": mail.correo,
            "sitios": sitios
        }

    except IntegrityError:
        db.rollback()
        return None
    finally:
        db.close()


# -----------------------------
# ACTUALIZAR MAIL
# -----------------------------
def actualizar_mail(mail_id, data):
    db = SessionLocal()
    try:
        mail = db.query(Mail).filter(Mail.id == mail_id).first()
        if mail is None:
            return None

        mail.nombre = data.get("nombre", mail.nombre)
        mail.correo = data.get("email", mail.correo)

        # borrar relaciones actuales
        db.query(SitioMail).filter(
            SitioMail.mail_id == mail_id
        ).delete()

        sitios = data.get("sitios")

        # 👉 TODOS los sitios
        if sitios is None:
            sitios_db = db.query(SitioWeb.id).all()
            sitios = [s[0] for s in sitios_db]

        for sitio_id in sitios:
            db.add(SitioMail(
                sitio_web_id=sitio_id,
                mail_id=mail_id
            ))

        db.commit()

        return {
            "id": mail.id,
            "nombre": mail.nombre,
            "email": mail.correo,
            "sitios": sitios
        }

    finally:
        db.close()


# -----------------------------
# ELIMINAR MAIL
# -----------------------------
def eliminar_mail(mail_id):
    db = SessionLocal()
    try:
        mail = db.query(Mail).filter(Mail.id == mail_id).first()
        if mail is None:
            return False

        db.delete(mail)
        db.commit()
        return True
    finally:
        db.close()



def obtener_mails_por_sitio(sitio_id):
    db = SessionLocal()
    try:
        mails = (
            db.query(Mail)
            .join(SitioMail, SitioMail.mail_id == Mail.id)
            .filter(SitioMail.sitio_web_id == sitio_id)
            .all()
        )

        return [
            {
                "id": m.id,
                "nombre": m.nombre,
                "email": m.correo
            }
            for m in mails
        ]
    finally:
        db.close()
