from sqlalchemy.orm import Session
from models import schemas, tables
from services.cache import cache
from services.hymn_service import invalidate_hymn_cache
from core.exceptions import HymnNotFoundError, CategoryNotFoundError, DatabaseError

CATEGORIES_CACHE_KEY = "all_categories"

def invalidate_categories_cache():
    """Invalidates the cache for the list of all categories."""
    cache.delete(CATEGORIES_CACHE_KEY)
    print("Cache invalidated for all categories.")

def get_categories(db: Session) -> list[schemas.Category]:
    """
    Retrieves a list of all categories from cache or database.
    """
    cached_categories_data = cache.get(CATEGORIES_CACHE_KEY)
    if cached_categories_data:
        print("Returning categories from cache.")
        return [schemas.Category.parse_obj(c) for c in cached_categories_data]

    print("Fetching categories from database.")
    categories = db.query(tables.Category).order_by(tables.Category.name).all()
    
    category_schemas = [schemas.Category.from_orm(c) for c in categories]
    cache.set(CATEGORIES_CACHE_KEY, [c.dict() for c in category_schemas], ex=3600)
    return category_schemas

def create_category(db: Session, category: schemas.CategoryCreate) -> tables.Category:
    """
    Creates a new category in the database.
    """
    try:
        db_category = tables.Category(name=category.name)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        invalidate_categories_cache()  # Invalidate cache after creation
        return db_category
    except Exception as e:
        db.rollback()
        raise DatabaseError(detail=f"Failed to create category: {e}")

def assign_category_to_hymn(db: Session, hymn_id: int, category_id: int):
    """
    Assigns a category to a hymn, raising an error if either does not exist.
    """
    try:
        hymn = db.query(tables.Hymn).filter(tables.Hymn.id == hymn_id).first()
        if not hymn:
            raise HymnNotFoundError(hymn_id=hymn_id)

        category = db.query(tables.Category).filter(tables.Category.id == category_id).first()
        if not category:
            raise CategoryNotFoundError(category_id=category_id)

        hymn.category_id = category_id
        db.commit()
        invalidate_hymn_cache(hymn_id=hymn_id)  # Invalidate specific hymn cache
        return {"message": "Category assigned successfully"}
    except Exception as e:
        db.rollback()
        raise DatabaseError(detail=f"Failed to assign category to hymn: {e}")
