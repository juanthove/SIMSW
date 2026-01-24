from sqlalchemy.exc import IntegrityError
from database.connection import SessionLocal
from database.models.detalleOZ_model import DetalleOZ
from database.models.informe_model import Informe

def obtener_detalles_oz():
    db = SessionLocal()
    try:
        detalles = db.query(DetalleOZ).all()
        return [d.to_dict() for d in detalles]
    finally:
        db.close()


def obtener_detalle_oz_por_id(detalle_id):
    db = SessionLocal()
    try:
        detalle = db.query(DetalleOZ).filter(
            DetalleOZ.id == detalle_id
        ).first()

        if detalle is None:
            return None

        return detalle.to_dict()
    finally:
        db.close()



def obtener_detalle_oz_por_informe(informe_id):
    db = SessionLocal()
    try:
        detalle = db.query(DetalleOZ).filter(
            DetalleOZ.informe_id == informe_id
        ).first()

        if detalle is None:
            return None

        return detalle.to_dict()
    finally:
        db.close()


def crear_detalle_oz(data):
    db = SessionLocal()
    try:
        detalle = DetalleOZ(
            endpoint=data.get("endpoint"),
            metodo=data.get("metodo"),
            parametro=data.get("parametro"),
            payload=data.get("payload"),
            informe_id=data.get("informe_id")
        )

        db.add(detalle)
        db.commit()
        db.refresh(detalle)

        return detalle.to_dict()

    except IntegrityError:
        db.rollback()
        return None
    finally:
        db.close()


def actualizar_detalle_oz(detalle_id, data):
    db = SessionLocal()
    try:
        detalle = db.query(DetalleOZ).filter(
            DetalleOZ.id == detalle_id
        ).first()

        if detalle is None:
            return None

        detalle.endpoint = data.get("endpoint", detalle.endpoint)
        detalle.metodo = data.get("metodo", detalle.metodo)
        detalle.parametro = data.get("parametro", detalle.parametro)
        detalle.payload = data.get("payload", detalle.payload)

        db.commit()
        db.refresh(detalle)

        return detalle.to_dict()
    finally:
        db.close()



def eliminar_detalle_oz(detalle_id):
    db = SessionLocal()
    try:
        detalle = db.query(DetalleOZ).filter(
            DetalleOZ.id == detalle_id
        ).first()

        if detalle is None:
            return False

        db.delete(detalle)
        db.commit()
        return True
    finally:
        db.close()



