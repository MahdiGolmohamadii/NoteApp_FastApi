from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app=app)

def test_get_root():
    reponse = client.get("/")
    assert reponse.status_code == 200
    assert reponse.json() == {"message": "we are live!"}

