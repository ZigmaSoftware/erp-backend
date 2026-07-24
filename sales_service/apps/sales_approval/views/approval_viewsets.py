from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.common_master.authentication.header_auth import GatewayHeaderAuthentication
from apps.sales_approval.serializers import ApprovalActionSerializer
from apps.sales_approval.services.customer_approval import CustomerApprovalService
from apps.sales_approval.services.sales_order_approval import SalesOrderApprovalService
from apps.sales_approval.services.freight_approval import FreightApprovalService
from apps.sales_approval.services.invoice_approval import InvoiceApprovalService
from apps.sales_approval.services.payable_approval import PayableApprovalService
from apps.sales_approval.services.afr_transport_approval import AfrTransportApprovalService
from apps.sales_approval.services.receivable_approval import ReceivableApprovalService
from apps.sales_approval.services.noc_verification import NocVerificationService
from apps.sales_shared.serializers import ApprovalHistorySerializer


class CustomerApprovalViewSet(GenericViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalActionSerializer
    lookup_field = "unique_id"

    def _svc(self):
        return CustomerApprovalService()

    def _user(self, request):
        return request.headers.get("X-User-Id", ""), request.headers.get("X-Username", "")

    def _respond(self, instance, action_label):
        return Response({"status": action_label, "unique_id": str(instance.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="site-approve")
    def site_approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve_site(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return self._respond(inst, "approved")

    @action(detail=True, methods=["post"], url_path="site-reject")
    def site_reject(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().reject_site(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return self._respond(inst, "rejected")

    @action(detail=True, methods=["post"], url_path="dept-approve")
    def dept_approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve_dept(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return self._respond(inst, "approved")

    @action(detail=True, methods=["post"], url_path="acc-approve")
    def acc_approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve_accounts(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return self._respond(inst, "approved")

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, **kwargs):
        h = self._svc().get_history(kwargs[self.lookup_field])
        return Response(ApprovalHistorySerializer(h, many=True).data)


class SalesOrderApprovalViewSet(GenericViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalActionSerializer
    lookup_field = "unique_id"

    def _svc(self):
        return SalesOrderApprovalService()

    def _user(self, request):
        return request.headers.get("X-User-Id", ""), request.headers.get("X-Username", "")

    def _respond(self, instance, label):
        return Response({"status": label, "unique_id": str(instance.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="site-approve")
    def site_approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve_site(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return self._respond(inst, "approved")

    @action(detail=True, methods=["post"], url_path="dept-approve")
    def dept_approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve_dept(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return self._respond(inst, "approved")

    @action(detail=True, methods=["post"], url_path="acc-approve")
    def acc_approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve_accounts(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return self._respond(inst, "approved")

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().reject(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "rejected", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, **kwargs):
        h = self._svc().get_history(kwargs[self.lookup_field])
        return Response(ApprovalHistorySerializer(h, many=True).data)


class AfrTransportApprovalViewSet(GenericViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalActionSerializer
    lookup_field = "unique_id"

    def _svc(self):
        return AfrTransportApprovalService()

    def _user(self, request):
        return request.headers.get("X-User-Id", ""), request.headers.get("X-Username", "")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "approved", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().reject(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "rejected", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="revert")
    def revert(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().revert(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "reverted", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, **kwargs):
        h = self._svc().get_history(kwargs[self.lookup_field])
        return Response(ApprovalHistorySerializer(h, many=True).data)


class ReceivableApprovalViewSet(GenericViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalActionSerializer
    lookup_field = "unique_id"

    def _svc(self):
        return ReceivableApprovalService()

    def _user(self, request):
        return request.headers.get("X-User-Id", ""), request.headers.get("X-Username", "")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "approved", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().reject(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "rejected", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, **kwargs):
        h = self._svc().get_history(kwargs[self.lookup_field])
        return Response(ApprovalHistorySerializer(h, many=True).data)


class NocVerificationViewSet(GenericViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalActionSerializer
    lookup_field = "unique_id"

    def _svc(self):
        return NocVerificationService()

    def _user(self, request):
        return request.headers.get("X-User-Id", ""), request.headers.get("X-Username", "")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "approved", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().reject(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "rejected", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, **kwargs):
        h = self._svc().get_history(kwargs[self.lookup_field])
        return Response(ApprovalHistorySerializer(h, many=True).data)


class FreightApprovalViewSet(GenericViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalActionSerializer
    lookup_field = "unique_id"

    def _svc(self):
        return FreightApprovalService()

    def _user(self, request):
        return request.headers.get("X-User-Id", ""), request.headers.get("X-Username", "")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "approved", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().reject(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "rejected", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, **kwargs):
        h = self._svc().get_history(kwargs[self.lookup_field])
        return Response(ApprovalHistorySerializer(h, many=True).data)


class InvoiceApprovalViewSet(GenericViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalActionSerializer
    lookup_field = "unique_id"

    def _svc(self):
        return InvoiceApprovalService()

    def _user(self, request):
        return request.headers.get("X-User-Id", ""), request.headers.get("X-Username", "")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "approved", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().reject(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "rejected", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, **kwargs):
        h = self._svc().get_history(kwargs[self.lookup_field])
        return Response(ApprovalHistorySerializer(h, many=True).data)


class PayableApprovalViewSet(GenericViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalActionSerializer
    lookup_field = "unique_id"

    def _svc(self):
        return PayableApprovalService()

    def _user(self, request):
        return request.headers.get("X-User-Id", ""), request.headers.get("X-Username", "")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().approve(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "approved", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sid, sname = self._user(request)
        inst = self._svc().reject(kwargs[self.lookup_field], sid, sname, ser.validated_data.get("remarks", ""), ser.validated_data.get("site_id"))
        return Response({"status": "rejected", "unique_id": str(inst.unique_id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, **kwargs):
        h = self._svc().get_history(kwargs[self.lookup_field])
        return Response(ApprovalHistorySerializer(h, many=True).data)
