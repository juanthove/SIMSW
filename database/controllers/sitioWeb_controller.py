from database.connection import SessionLocal
from database.models.sitioWeb_model import SitioWeb
from sqlalchemy.exc import IntegrityError

# Obtener todos los sitios
def obtener_sitios():
    db = SessionLocal()
    try:
        sitios = db.query(SitioWeb).all()
        return [s.to_dict() for s in sitios]
    finally:
        db.close()


# Obtener un sitio por ID
def obtener_sitio_por_id(sitio_id):
    db = SessionLocal()
    try:
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_id).first()
        return sitio.to_dict() if sitio else None
    finally:
        db.close()


# Crear sitio web
def crear_sitio(data):
    db = SessionLocal()
    try:
        sitio = SitioWeb(
            nombre=data.get("nombre"),
            url=data.get("url"),
            propietario=data.get("propietario")
        )

        db.add(sitio)
        db.commit()
        db.refresh(sitio)

        return sitio.to_dict()

    except IntegrityError:
        db.rollback()
        raise ValueError("URL_DUPLICADA")

    finally:
        db.close()



#Actualizar sitio web
def actualizar_sitio(sitio_id, data):
    db = SessionLocal()
    try:
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_id).first()

        if sitio is None:
            return None

        # Actualizar solo los campos permitidos
        if "nombre" in data:
            sitio.nombre = data["nombre"]

        if "url" in data:
            sitio.url = data["url"]

        if "propietario" in data:
            sitio.propietario = data["propietario"]

        db.commit()
        db.refresh(sitio)

        return sitio.to_dict()

    except IntegrityError:
        db.rollback()
        raise ValueError("URL_DUPLICADA")
    finally:
        db.close()


#Eliminar un sitio web
def eliminar_sitio(sitio_id):
    db = SessionLocal()
    try:
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_id).first()

        if sitio is None:
            return False

        db.delete(sitio)
        db.commit()

        return True
    finally:
        db.close()