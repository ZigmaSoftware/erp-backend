from django.urls import path
from gateway.views.proxy import MasterServiceProxy, AuthServiceProxy
from gateway.views.debug import DebugEchoView

urlpatterns = [
    path("api/master-service/<path:path>", MasterServiceProxy.as_view()),
    path("api/auth-service/<path:path>", AuthServiceProxy.as_view()),
    path("api/debug/echo/", DebugEchoView.as_view()),
]
