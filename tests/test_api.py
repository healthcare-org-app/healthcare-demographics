from app.routes import RESOURCE
from app.census_geocoder import GeocoderUnavailable
from app.purgomalum import ProfanityFilterUnavailable


def test_crud(client, svc):
    r = client.post(f"/api/{RESOURCE}/", json={"name": "test"})
    assert r.status_code == 201, r.data
    rid = r.get_json()["id"]

    r = client.get(f"/api/{RESOURCE}/{rid}")
    assert r.status_code == 200

    r = client.patch(f"/api/{RESOURCE}/{rid}", json={"name": "updated"})
    assert r.status_code == 200
    assert r.get_json()["name"] == "updated"

    r = client.delete(f"/api/{RESOURCE}/{rid}")
    assert r.status_code == 200

    r = client.get(f"/api/{RESOURCE}/")
    body = r.get_json()
    assert body["count"] >= 1


def test_get_missing(client):
    r = client.get(f"/api/{RESOURCE}/999999")
    assert r.status_code == 404


def test_audit_emitted_on_create(client, svc):
    client.post(f"/api/{RESOURCE}/", json={"name": "audit-me"})
    topics = [t for t, _, _ in svc.bus.published]
    assert "audit.event" in topics


def test_validate_address_match(client, monkeypatch):
    monkeypatch.setattr("app.routes.geocode_address", lambda *a, **kw: [
        {"matched_address": "4600 SILVER HILL RD, WASHINGTON, DC, 20233",
         "latitude": 38.845, "longitude": -76.928, "city": "WASHINGTON", "state": "DC", "zip": "20233"},
    ])
    r = client.post(f"/api/{RESOURCE}/validate-address", json={"address": "4600 Silver Hill Rd, Washington, DC 20233"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["valid"] is True
    assert body["latitude"] == 38.845


def test_validate_address_no_match(client, monkeypatch):
    monkeypatch.setattr("app.routes.geocode_address", lambda *a, **kw: [])
    r = client.post(f"/api/{RESOURCE}/validate-address", json={"address": "not a real place"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["valid"] is False
    assert body["latitude"] is None


def test_validate_address_missing_field(client):
    r = client.post(f"/api/{RESOURCE}/validate-address", json={})
    assert r.status_code == 400


def test_validate_address_geocoder_down(client, monkeypatch):
    def _boom(*a, **kw):
        raise GeocoderUnavailable("network down")
    monkeypatch.setattr("app.routes.geocode_address", _boom)
    r = client.post(f"/api/{RESOURCE}/validate-address", json={"address": "123 Main St"})
    assert r.status_code == 502


def test_filter_text_changed(client, monkeypatch):
    monkeypatch.setattr("app.routes.filter_text", lambda text, **kw: text.replace("damn", "****"))
    r = client.post(f"/api/{RESOURCE}/filter-text", json={"text": "this damn form"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["filtered"] == "this **** form"
    assert body["changed"] is True


def test_filter_text_unchanged(client, monkeypatch):
    monkeypatch.setattr("app.routes.filter_text", lambda text, **kw: text)
    r = client.post(f"/api/{RESOURCE}/filter-text", json={"text": "perfectly clean text"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["changed"] is False


def test_filter_text_missing_field(client):
    r = client.post(f"/api/{RESOURCE}/filter-text", json={})
    assert r.status_code == 400


def test_filter_text_provider_down(client, monkeypatch):
    def _boom(*a, **kw):
        raise ProfanityFilterUnavailable("network down")
    monkeypatch.setattr("app.routes.filter_text", _boom)
    r = client.post(f"/api/{RESOURCE}/filter-text", json={"text": "some text"})
    assert r.status_code == 502
