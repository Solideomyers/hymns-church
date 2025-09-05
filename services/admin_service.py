from sqlalchemy.orm import Session
from models.tables import ContentLine, HymnContent, Hymn, Category

def reset_database(db: Session):
    """
    Elimina todos los datos de las tablas principales del himnario, manteniendo la estructura y migraciones.
    """
    # El orden importa por las relaciones (hijos primero)
    db.query(ContentLine).delete()
    db.query(HymnContent).delete()
    db.query(Hymn).delete()
    db.query(Category).delete()
    db.commit()
    return {"message": "Base de datos limpiada exitosamente."}
