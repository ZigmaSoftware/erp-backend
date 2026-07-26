import requests

from django.conf import settings


def _gateway_headers(request=None) -> dict[str, str]:
    headers = {}
    if request is None:
        return headers
    for src, dst in [
        ("HTTP_X_USER_ID", "X-User-Id"),
        ("HTTP_X_USERNAME", "X-Username"),
        ("HTTP_X_GROUPS", "X-Groups"),
        ("HTTP_AUTHORIZATION", "Authorization"),
    ]:
        val = request.META.get(src)
        if val:
            headers[dst] = val
    return headers


def resolve_site_names(site_ids: set[str], request=None) -> dict[str, str]:
    if not site_ids:
        return {}

    base_url = getattr(settings, "MASTER_SERVICE_API_URL", "http://127.0.0.1:8002")
    auth_headers = _gateway_headers(request)

    result: dict[str, str] = {}
    url = f"{base_url}/v1/masters/sites/?include_deleted=true&limit=100"

    while url:
        try:
            resp = requests.get(url, headers=auth_headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException:
            break

        items = data.get("results") if isinstance(data, dict) else data
        if isinstance(items, list):
            for item in items:
                uid = str(item["unique_id"])
                if uid in site_ids:
                    result[uid] = item.get("site_name") or item.get("name", "")
            # if we already have all the requested ids, stop early
            if result.keys() >= site_ids:
                break

        url = data.get("next") if isinstance(data, dict) else None

    return result
