#!/bin/bash

BASE="$HOME/zigma-erp/erp-backend"

source "$BASE/venv/bin/activate"

(cd "$BASE/api_gateway" && python manage.py runserver 8000) &
(cd "$BASE/auth_service" && python manage.py runserver 8001) &
(cd "$BASE/master-service" && python manage.py runserver 8002) &
(cd "$BASE/sales_service" && python manage.py runserver 8003) &

wait