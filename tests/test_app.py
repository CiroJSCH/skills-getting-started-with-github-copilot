from urllib.parse import quote

from src.app import activities


def signup_url(activity_name):
    return f"/activities/{quote(activity_name, safe='')}/signup"


def test_root_redirects_to_frontend(client):
    response = client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client):
    email = "new-student@mergington.edu"

    response = client.post(signup_url("Soccer Team"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Soccer Team"}
    assert email in client.get("/activities").json()["Soccer Team"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        signup_url("Chess Club"),
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        signup_url("Unknown Activity"),
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete(signup_url("Chess Club"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        signup_url("Unknown Activity"),
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        signup_url("Chess Club"),
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
