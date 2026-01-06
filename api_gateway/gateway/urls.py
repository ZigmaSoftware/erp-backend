from django.urls import path
from gateway.views.proxy import MasterServiceProxy
from gateway.views.debug import DebugEchoView

urlpatterns = [
    path("api/master/<path:path>", MasterServiceProxy.as_view()),
    path("api/debug/echo/", DebugEchoView.as_view()),
]
