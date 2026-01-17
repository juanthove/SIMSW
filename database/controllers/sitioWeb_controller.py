from database.connection import SessionLocal
from database.models.sitioWeb_model import SitioWeb
from database.models.analisis_model import Analisis
from database.models.informe_model import Informe
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

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


#Obtener sitios con cantidad de analisis y fecha del ultimo
def obtener_sitios_con_resumen():
    db = SessionLocal()
    try:
        resultados = db.query(
            SitioWeb.id,
            SitioWeb.nombre,
            SitioWeb.url,
            func.count(Analisis.id).label("cantAnalisis"),
            func.max(Analisis.fecha).label("ultimoAnalisis")
        ).outerjoin(
            Analisis, Analisis.sitio_web_id == SitioWeb.id
        ).group_by(
            SitioWeb.id
        ).all()

        return [
            {
                "id": r.id,
                "nombre": r.nombre,
                "url": r.url,
                "cantAnalisis": r.cantAnalisis,
                "ultimoAnalisis": (
                    r.ultimoAnalisis.isoformat()
                    if r.ultimoAnalisis else None
                )
            }
            for r in resultados
        ]
    finally:
        db.close()


#Obtener informacion del sitio y de sus analisis
def obtener_detalle_sitio(sitio_id):
    db = SessionLocal()
    try:
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_id).first()

        if not sitio:
            return None

        analisis = (
            db.query(Analisis)
            .filter(Analisis.sitio_web_id == sitio_id)
            .order_by(Analisis.fecha.desc())
            .all()
        )

        resultado = []

        for a in analisis:
            cantidad_informes = (
                db.query(func.count(Informe.id))
                .filter(Informe.analisis_id == a.id)
                .scalar()
            )

            resultado.append({
                "id": a.id,
                "nombre": a.nombre,
                "estado": a.estado,
                "tipo": a.tipo,
                "resultado_global": a.resultado_global,
                "fecha": a.fecha.isoformat(),
                "cantidad_informes": cantidad_informes
            })

        return {
            "siteId": sitio.id,
            "nombre": sitio.nombre,
            "url": sitio.url,
            "propietario": sitio.propietario,
            "analisis": resultado
        }

    finally:
        db.close()