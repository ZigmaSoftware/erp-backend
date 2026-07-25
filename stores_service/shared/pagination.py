import math
from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class LimitOffsetWithPage(LimitOffsetPagination):
    """
    Limit/Offset pagination with support for:
    - ?page= (1-based page number)
    - ?limit=
    - ?offset=

    Returns extra metadata:
    - page
    - total_pages
    """

    default_limit = 10
    max_limit = 100

    def paginate_queryset(self, queryset, request, view=None):
        """
        Accept either:
        - ?limit=5&offset=10
        OR
        - ?page=2&limit=5

        If page is provided and offset is not,
        compute offset safely.
        """

        page_param = request.query_params.get("page")
        offset_param = request.query_params.get(self.offset_query_param)

        # If user provided page but NOT offset
        if page_param and not offset_param:
            try:
                page = max(int(page_param), 1)
            except (TypeError, ValueError):
                page = 1

            # Get correct limit
            limit = self.get_limit(request)
            if limit is None:
                limit = self.default_limit

            # SAFE offset calculation
            computed_offset = (page - 1) * limit

            # Inject computed offset into request
            mutable_query_params = request._request.GET.copy()
            mutable_query_params[self.offset_query_param] = str(computed_offset)
            request._request.GET = mutable_query_params

        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """
        Return paginated response with page metadata.
        """

        limit = self.limit or self.default_limit

        # Avoid division by zero
        if not limit:
            limit = 1

        current_page = (self.offset // limit) + 1
        total_pages = math.ceil(self.count / limit) if self.count else 1

        return Response(
            OrderedDict(
                [
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("page", current_page),
                    ("total_pages", total_pages),
                    ("results", data),
                ]
            )
        )
