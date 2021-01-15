from rest_framework import pagination
from rest_framework.response import Response

class CustomPagination(pagination.LimitOffsetPagination):
    limit_query_param='limit'
    offset_query_param='offset'

    