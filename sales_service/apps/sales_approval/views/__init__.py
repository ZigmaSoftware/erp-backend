from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.common_master.authentication.header_auth import GatewayHeaderAuthentication
from apps.sales_approval.serializers import ApprovalActionSerializer


class WorkOrderApprovalViewSet(GenericViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalActionSerializer
    lookup_field = "unique_id"

    def _get_service(self):
        from apps.sales_approval.services.work_order_approval import WorkOrderApprovalService
        return WorkOrderApprovalService()

    def _get_approver(self, request):
        return (
            request.headers.get("X-User-Id", ""),
            request.headers.get("X-Username", ""),
        )

    @action(detail=True, methods=["post"], url_path="dtc-approve")
    def dtc_approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._get_approver(request)
        instance = self._get_service().approve_dtc(
            entity_unique_id=kwargs[self.lookup_field],
            approver_id=sid, approver_name=sname,
            remarks=ser.validated_data.get("remarks", ""),
            site_id=ser.validated_data.get("site_id"),
        )
        return Response({"status": "approved", "unique_id": str(instance.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="gm-approve")
    def gm_approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._get_approver(request)
        instance = self._get_service().approve_gm(
            entity_unique_id=kwargs[self.lookup_field],
            approver_id=sid, approver_name=sname,
            remarks=ser.validated_data.get("remarks", ""),
            site_id=ser.validated_data.get("site_id"),
        )
        return Response({"status": "approved", "unique_id": str(instance.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="director-approve")
    def director_approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._get_approver(request)
        instance = self._get_service().approve_director(
            entity_unique_id=kwargs[self.lookup_field],
            approver_id=sid, approver_name=sname,
            remarks=ser.validated_data.get("remarks", ""),
            site_id=ser.validated_data.get("site_id"),
        )
        return Response({"status": "approved", "unique_id": str(instance.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="send")
    def send_wo(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._get_approver(request)
        instance = self._get_service().send_work_order(
            entity_unique_id=kwargs[self.lookup_field],
            approver_id=sid, approver_name=sname,
            remarks=ser.validated_data.get("remarks", ""),
            site_id=ser.validated_data.get("site_id"),
        )
        return Response({"status": "sent", "unique_id": str(instance.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, **kwargs):
        from apps.sales_shared.serializers import ApprovalHistorySerializer
        history = self._get_service().get_history(kwargs[self.lookup_field])
        return Response(ApprovalHistorySerializer(history, many=True).data)
