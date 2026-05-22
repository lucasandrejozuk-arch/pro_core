from __future__ import annotations

import httpx

from frontend.app.core.backend_health import BackendHealthProbe, health_url_from_api_base


def test_health_url_uses_backend_root_instead_of_api_prefix() -> None:
    assert (
        health_url_from_api_base("http://127.0.0.1:8000/api/v1")
        == "http://127.0.0.1:8000/health"
    )
    assert (
        health_url_from_api_base("http://127.0.0.1:8000/pro-core/api/v1/")
        == "http://127.0.0.1:8000/pro-core/health"
    )


def test_backend_health_probe_reports_connected_only_for_ok_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/health"
        return httpx.Response(200, json={"status": "ok"})

    probe = BackendHealthProbe(
        "http://127.0.0.1:8000/api/v1",
        transport=httpx.MockTransport(handler),
    )

    status = probe.check()
    probe.close()

    assert status.is_connected is True
    assert status.message == "Backend: conectado"


def test_backend_health_probe_does_not_report_http_500_as_connected() -> None:
    probe = BackendHealthProbe(
        "http://127.0.0.1:8000/api/v1",
        transport=httpx.MockTransport(lambda request: httpx.Response(500)),
    )

    status = probe.check()
    probe.close()

    assert status.is_connected is False
    assert status.message == "Backend: erro 500"


def test_backend_health_probe_rejects_degraded_payload() -> None:
    probe = BackendHealthProbe(
        "http://127.0.0.1:8000/api/v1",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"status": "down"})),
    )

    status = probe.check()
    probe.close()

    assert status.is_connected is False
    assert status.message == "Backend: health degradado"

