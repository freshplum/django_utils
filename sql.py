from django.db import connections, transaction, backend

def select_sql(sql, db='tron'):
    cursor = connections[db].cursor()
    cursor.execute(sql)
    transaction.commit_unless_managed(using=db)
    return dictfetchall(cursor)

def cursor_sql(sql, db='tron'):
    cursor = connections[db].cursor()
    cursor.execute(sql)
    transaction.commit_unless_managed(using=db)
    return cursor

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]