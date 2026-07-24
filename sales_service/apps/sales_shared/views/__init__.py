from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common_master.authentication.header_auth import GatewayHeaderAuthentication
from apps.sales_shared.models.approval_status import ApprovalHistory
from apps.sales_shared.serializers import ApprovalHistorySerializer


class ApprovalHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for approval history.
    Query params: ?entity_type=work_order&entity_id=<uuid>
    """

    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalHistorySerializer
    lookup_field = "unique_id"

    def get_queryset(self):
        qs = ApprovalHistory.objects.all()
        entity_type = self.request.query_params.get("entity_type")
        if entity_type:
            qs = qs.filter(entity_type=entity_type)
        entity_id = self.request.query_params.get("entity_id")
        if entity_id:
            qs = qs.filter(entity_id=entity_id)
        return qs
