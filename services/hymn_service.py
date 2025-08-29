from psycopg2.extensions import connection
from ..models import schemas

def get_hymns(db: connection):
    with db.cursor() as cursor:
        cursor.execute("SELECT id, hymn_number, title, category_id FROM hymns")
        hymns = cursor.fetchall()
        return [schemas.Hymn(id=h[0], hymn_number=h[1], title=h[2], category_id=h[3]) for h in hymns]

def get_hymn(db: connection, hymn_id: int):
    with db.cursor() as cursor:
        cursor.execute("SELECT id, hymn_number, title, category_id FROM hymns WHERE id = %s", (hymn_id,))
        hymn = cursor.fetchone()
        if hymn:
            hymn_model = schemas.Hymn(id=hymn[0], hymn_number=hymn[1], title=hymn[2], category_id=hymn[3])

            cursor.execute("SELECT id, hymn_id, content_type, stanza_number, content_order FROM hymn_content WHERE hymn_id = %s ORDER BY content_order", (hymn_id,))
            contents = cursor.fetchall()
            for content in contents:
                content_model = schemas.HymnContent(id=content[0], hymn_id=content[1], content_type=content[2], stanza_number=content[3], content_order=content[4])

                cursor.execute("SELECT id, hymn_content_id, line_text, line_order FROM content_lines WHERE hymn_content_id = %s ORDER BY line_order", (content_model.id,))
                lines = cursor.fetchall()
                for line in lines:
                    content_model.lines.append(schemas.ContentLine(id=line[0], hymn_content_id=line[1], line_text=line[2], line_order=line[3]))
                
                hymn_model.content.append(content_model)

            return hymn_model
    return None
