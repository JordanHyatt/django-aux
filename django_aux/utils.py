
from django.db import connection, ProgrammingError
import string
import random
import logging
logger = logging.getLogger(__name__)


class PasswordUtils:
    AMBIGUOUS_CHARS = ['0', 'O', 'l', 'I', 'o']

    def __init__(self, valid_symbols=None):
        if valid_symbols == None:
            self.valid_symbols = ['!','$','#','^']
        else: 
            self.valid_symbols = valid_symbols

    def check_password(
        self, password, min_length=12, must_have_symbol=True, must_have_caps=True, must_have_digit=True
    ):
        pset = set(password)
        assert len(password) >= min_length, f"Password must be at least {min_length} characters"
        assert len(pset.intersection(string.ascii_lowercase)) > 0, f"Password must contain at least 1 lowercase letter"
        if must_have_symbol:
            assert len(pset.intersection(self.valid_symbols)) > 0, f"Password must contain at least 1 special character {self.valid_symbols}"
        if must_have_caps:
            assert len(pset.intersection(string.ascii_uppercase)) > 0, f"Password must contain at least 1 uppercase letter"
        if must_have_digit:
            assert len(pset.intersection(string.digits)) > 0, f"Password must contain at least 1 digit {string.digits}"
        return True


    def generate_password(self, N=15, include_symbols=True, remove_ambiguous=True):
        all = string.ascii_letters + string.digits 
        if include_symbols:
            all += ''.join(self.valid_symbols) * 3
        if remove_ambiguous:
            for bad in self.AMBIGUOUS_CHARS:
                all = all.replace(bad,'')
        return ''.join(random.sample(all, N))




def create_view_from_qs(qs, view_name, materialized=True, ufields=None, owner='postgres', sql_permissions='', read_only_users=None,):
    """Utility function to create a DB view from a django queryset.
    Args:
        qs (django.db.QuerySet): The queryset to be translated into a view
        view_name (str): View name to be created/updated
        materialized (bool): If True will create a materialized view. default True
        ufields (list): List of field names to create a unique index on
        sql_permissions (str, optional): SQL to be executed after the view is created,
            intended for setting permissions but could be any raw SQL.
            i.e. ALTER TABLE public.{view_name} OWNER TO postgres;
        read_only_users (list, optional): List of usernames to grant read-only permisions to. 
            these will be added to the sql_permissions paramter. defaults to []
    """    
    if not materialized and ufields:
        raise AssertionError("Unique indexes only allowed on materialized views")
    if not read_only_users:
        read_only_users = []
    qstr, params = qs.query.sql_with_params()
    vstr = 'MATERIALIZED VIEW' if materialized else 'VIEW'
    drop_qstr1 = f''' DROP VIEW IF EXISTS "{view_name}" '''
    drop_qstr2 = f''' DROP MATERIALIZED VIEW IF EXISTS "{view_name}" '''
    qstr = f''' CREATE {vstr} "{view_name}" AS {qstr} '''
    index_qstr = None
    if ufields:
        index_name = f'unique_{view_name}'
        index_drop = f"DROP INDEX IF EXISTS {index_name}"
        index_qstr = f"CREATE UNIQUE INDEX {index_name} ON {view_name} ({', '.join(ufields)})"
    with connection.cursor() as cursor:
        # Drop existing view (materialized or regular) with the name view_name
        for dstr in [drop_qstr1, drop_qstr2]:
            try:
                cursor.execute(dstr)
            except ProgrammingError:
                pass
        # main view creation
        cursor.execute(qstr, params)
        # unique index creation
        if index_qstr:
            cursor.execute(index_drop)
            cursor.execute(index_qstr)

    std_perms = f'''
        ALTER TABLE public.{view_name} OWNER TO {owner};
        GRANT ALL ON TABLE public.{view_name} TO {owner};
    '''
    with connection.cursor() as cursor:
        cursor.execute(std_perms)

    for ruser in read_only_users:
        sql_permissions += f''' GRANT SELECT ON TABLE public.{view_name} TO {ruser}; '''  

    if sql_permissions:
        with connection.cursor() as cursor:
            cursor.execute(sql_permissions)
