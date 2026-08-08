from fastapi.testclient import TestClient
from main import app, startup

client = TestClient(app)

startup()

# 1. Claiming a PENDING case succeeds and transitions its status.
def test_claim_pending_case():

    response = client.post(
        "/cases/1/claim",
        json={"claimedBy": "jsmith"}
    )

    assert response.status_code == 200

    case = response.json()

    assert case["status"] == "IN_PROGRESS"
    assert case["claimedBy"] == 1
    assert case["claimedAt"] is not None

# 2. Claiming a case that is already IN_PROGRESS or COMPLETED returns an error.
def test_claim_in_progress_case():

    response = client.post(
        "/cases/3/claim",
        json={"claimedBy": "jsmith"}
    )

    assert response.status_code == 400

def test_claim_completed_case():

    response = client.post(
        "/cases/4/claim",
        json={"claimedBy": "jsmith"}
    )

    assert response.status_code == 400

# 3. Claiming a case with a missing or unknown username returns an error.
def test_claim_missing_username():

    response = client.post(
        "/cases/1/claim",
        json={}
    )

    assert response.status_code == 400


def test_claim_unknown_username():

    response = client.post(
        "/cases/1/claim",
        json={"claimedBy": "paulyarin"}
    )

    assert response.status_code == 400

# 4. Submitting a report on an IN_PROGRESS case succeeds.
def test_submit_report():

    # Case 3 is already IN_PROGRESS and was claimed by jsmith
    response = client.post(
        "/cases/3/report",
        json={
            "author": "jsmith",
            "report": "The patient has some things going on with xyz"
        }
    )

    assert response.status_code == 200

    case = response.json()

    assert case["status"] == "COMPLETED"
    assert case["report"] == "The patient has some things going on with xyz"

# 5. Submitting a report on a PENDING or COMPLETED case returns an error.
def test_submit_report_on_pending_case():

    response = client.post(
        "/cases/2/report",
        json={
            "author": "jsmith",
            "report": "Some findings"
        }
    )

    assert response.status_code == 400


def test_submit_report_on_completed_case():

    response = client.post(
        "/cases/4/report",
        json={
            "author": "adoe",
            "report": "Some findings"
        }
    )

    assert response.status_code == 400

# 6. Submitting a report with an empty body returns a validation error.
def test_submit_empty_report():

    response = client.post(
        "/cases/3/report",
        json={
            "author": "jsmith",
            "report": ""
        }
    )

    assert response.status_code == 400

# 7. Submitting a report as an employee other than the one who claimed the case returns an error.
def test_submit_report_wrong_employee():

    # Case 6 was claimed by bwilliams (employee 3)
    response = client.post(
        "/cases/6/report",
        json={
            "author": "jsmith",
            "report": "Some findings"
        }
    )

    assert response.status_code == 400