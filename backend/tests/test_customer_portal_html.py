from fastapi.testclient import TestClient

from backend.app.main import app


def test_customer_portal_html_delivery():
    client = TestClient(app)
    response = client.get("/customer-portal")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert (
        "CSP" not in response.headers
        or "default-src" in response.headers["Content-Security-Policy"]
    )
    assert 'id="theme-toggle"' in response.text
    assert "Acesso seguro" in response.text
