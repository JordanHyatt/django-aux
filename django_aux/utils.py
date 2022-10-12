
from django.db import connection

def create_view_from_qs(qs, view_name, sql_permissions=None):
    """Utility function to create a DB view from a queryset.

    Args:
        qs (django.db.QuerySet): The queryset to be translated into a view
        view_name (str): View name to be created/updated
        sql_permissions (str, optional): SQL to be executed after the view is created, 
            intended for setting permissions but could be anything. 
            i.e. ALTER TABLE public.{view_name} OWNER TO postgres;
    """    
    qstr, params = qs.query.sql_with_params()
    drop_qstr = f''' DROP VIEW IF EXISTS "{view_name}" '''
    qstr = f''' CREATE OR REPLACE VIEW "{view_name}" AS {qstr} '''
    with connection.cursor() as cursor:
        cursor.execute(drop_qstr)
        cursor.execute(qstr, params)
    if sql_permissions:
        with connection.cursor() as cursor:
            cursor.execute(sql_permissions)





