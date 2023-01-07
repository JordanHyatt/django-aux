from django_tables2 import Table
from request.models import Request


class RequestTable(Table):
    ''' Table for displaying user http request instances '''

    class Meta:
        model = Request
        exclude = []
        sequence = []