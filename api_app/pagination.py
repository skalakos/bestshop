from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import CatalogFilter


class PaginationClass(PageNumberPagination):
    page_size = 3
    page_query_param = "currentPage"

    def get_paginated_response(self, data):
        return Response(
            {
                "items": data,
                "currentPage": self.page.number,
                "lastPage": self.page.paginator.num_pages,
            }
        )
