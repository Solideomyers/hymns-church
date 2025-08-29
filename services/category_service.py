from psycopg2.extensions import connection
from ..models import schemas

def get_categories(db: connection):
    with db.cursor() as cursor:
        cursor.execute("SELECT id, name FROM categories")
        categories = cursor.fetchall()
        return [schemas.Category(id=c[0], name=c[1]) for c in categories]

def create_category(db: connection, category: schemas.Category):
    with db.cursor() as cursor:
        cursor.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id", (category.name,))
        new_id = cursor.fetchone()[0]
        db.commit()
        return schemas.Category(id=new_id, name=category.name)

def assign_category_to_hymn(db: connection, hymn_id: int, category_id: int):
    with db.cursor() as cursor:
        cursor.execute("UPDATE hymns SET category_id = %s WHERE id = %s", (category_id, hymn_id))
        db.commit()
    return {"message": "Category assigned successfully"}
