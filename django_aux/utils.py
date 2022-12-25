
from django.db import connection
import string
import random


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




def create_view_from_qs(qs, view_name, sql_permissions=None):
    """Utility function to create a DB view from a django queryset.

    Args:
        qs (django.db.QuerySet): The queryset to be translated into a view
        view_name (str): View name to be created/updated
        sql_permissions (str, optional): SQL to be executed after the view is created, 
            intended for setting permissions but could be any raw SQL. 
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





