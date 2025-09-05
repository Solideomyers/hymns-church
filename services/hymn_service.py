from sqlalchemy.orm import Session, joinedload
from models import schemas, tables
from services.cache import cache
from core.exceptions import HymnNotFoundError, DatabaseError

HYMNS_CACHE_KEY = "all_hymns"
HYMN_DETAIL_CACHE_KEY_PREFIX = "hymn_detail_"

def invalidate_hymn_cache(hymn_id: int = None):
    """
    Invalidate hymn-related caches.
    If hymn_id is provided, invalidates the cache for that specific hymn.
    Always invalidates the cache for the list of all hymns.
    """
    cache.delete(HYMNS_CACHE_KEY)
    if hymn_id:
        cache.delete(f"{HYMN_DETAIL_CACHE_KEY_PREFIX}{hymn_id}")
    print(f"Cache invalidated for all hymns and hymn_id: {hymn_id}")

def get_hymns(db: Session):
    """
    Retrieves a list of all hymns from cache or database.
    """
    cached_hymns_data = cache.get(HYMNS_CACHE_KEY)
    if cached_hymns_data:
        print("Returning hymns from cache.")
        return [schemas.Hymn.parse_obj(h) for h in cached_hymns_data]

    print("Fetching hymns from database.")
    hymns = db.query(tables.Hymn).order_by(tables.Hymn.hymn_number).all()
    
    hymn_schemas = [schemas.Hymn.from_orm(h) for h in hymns]
    cache.set(HYMNS_CACHE_KEY, [h.dict() for h in hymn_schemas], ex=3600)
    return hymn_schemas

def get_hymn(db: Session, hymn_id: int):
    """
    Retrieves a specific hymn by its ID, including its full content.
    """
    cache_key = f"{HYMN_DETAIL_CACHE_KEY_PREFIX}{hymn_id}"
    cached_hymn_data = cache.get(cache_key)
    if cached_hymn_data:
        print(f"Returning hymn {hymn_id} from cache.")
        return schemas.Hymn.parse_obj(cached_hymn_data)

    print(f"Fetching hymn {hymn_id} from database.")
    hymn = (
        db.query(tables.Hymn)
        .options(joinedload(tables.Hymn.content).joinedload(tables.HymnContent.lines))
        .filter(tables.Hymn.id == hymn_id)
        .first()
    )

    if not hymn:
        raise HymnNotFoundError(hymn_id=hymn_id)

    hymn_schema = schemas.Hymn.from_orm(hymn)
    cache.set(cache_key, hymn_schema.dict(), ex=3600)
    return hymn_schema
        

def create_or_update_hymns_from_parsed_data(db: Session, hymns_data: list):
    """
    Creates or updates hymns in the database from parsed data.
    This is more robust than the previous DELETE then INSERT logic.
    """
    try:
        for hymn_data in hymns_data:
            db_hymn = db.query(tables.Hymn).filter_by(hymn_number=hymn_data['numero']).first()

            if db_hymn:
                # Update existing hymn
                db_hymn.title = hymn_data['titulo']
                # Clear existing content to replace it
                db_hymn.content.clear()
                invalidate_hymn_cache(hymn_id=db_hymn.id)
            else:
                # Create new hymn
                db_hymn = tables.Hymn(
                    hymn_number=hymn_data['numero'],
                    title=hymn_data['titulo']
                )
                db.add(db_hymn)

            # Add new content
            for i, content_item in enumerate(hymn_data['contenido']):
                db_content = tables.HymnContent(
                    hymn=db_hymn,
                    content_type=content_item['tipo'],
                    stanza_number=content_item.get('estrofa_num'),
                    content_order=i
                )
                db.add(db_content)

                for j, line_text in enumerate(content_item['texto']):
                    db_line = tables.ContentLine(
                        hymn_content=db_content,
                        line_text=line_text,
                        line_order=j
                    )
                    db.add(db_line)

        db.commit()
        print(f"Successfully created/updated data for {len(hymns_data)} hymns.")
        invalidate_hymn_cache() # Invalidate the main list cache

    except Exception as e:
        db.rollback()
        raise DatabaseError(detail=f"Failed to create or update hymns: {e}")