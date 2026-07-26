# Runs every backend service with one command: `honcho start` (from erp-backend/).
# Ports here must match AUTH_SERVICE_URL / MASTER_SERVICE_URL / SALES_SERVICE_URL
# in erp-backend/.env - that's what the gateway uses to reach each service.
#
# To add a new service later: run it on its own port, add one line below,
# and wire it into api_gateway (see SERVICE_URLS in
# api_gateway/config/settings.py + api_gateway/gateway/urls.py).

gateway: cd api_gateway && python manage.py runserver 0.0.0.0:8000
auth:    cd auth_service && python manage.py runserver 0.0.0.0:8001
master:  cd master-service && python manage.py runserver 0.0.0.0:8003
sales:   cd sales_service && python manage.py runserver 0.0.0.0:8004
