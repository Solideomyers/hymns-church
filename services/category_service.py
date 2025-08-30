from psycopg2.extensions import connection
from ..models import schemas
from .cache import cache
from .hymn_service import invalidate_hymn_cache

CATEGORIES_CACHE_KEY = "all_categories"

def invalidate_categories_cache():
    cache.delete(CATEGORIES_CACHE_KEY)

def get_categories(db: connection):
    cached_categories = cache.get(CATEGORIES_CACHE_KEY)
    if cached_categories:
        print("Returning categories from cache.")
        return [schemas.Category(**c) for c in cached_categories]

    with db.cursor() as cursor:
        cursor.execute("SELECT id, name FROM categories")
        categories = cursor.fetchall()
        category_list = [schemas.Category(id=c[0], name=c[1]) for c in categories]
        cache.set(CATEGORIES_CACHE_KEY, [c.dict() for c in category_list], ex=3600) # Cache for 1 hour
        return category_list

def create_category(db: connection, category: schemas.Category):
    with db.cursor() as cursor:
        cursor.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id", (category.name,))
        new_id = cursor.fetchone()[0]
        db.commit()
        invalidate_categories_cache() # Invalidate cache after creating a new category
        return schemas.Category(id=new_id, name=category.name)

def assign_category_to_hymn(db: connection, hymn_id: int, category_id: int):
    with db.cursor() as cursor:
        cursor.execute("UPDATE hymns SET category_id = %s WHERE id = %s", (category_id, hymn_id))
        db.commit()
    invalidate_hymn_cache() # Invalidate hymn cache when a hymn's category is updated
    return {"message": "Category assigned successfully"}
