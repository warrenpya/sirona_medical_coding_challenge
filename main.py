import uvicorn
from fastapi import FastAPI, HTTPException
from datetime import datetime

app = FastAPI()

cases = []
employees = []
next_employee_id = 4

@app.on_event("startup")
def startup():
    global cases
    global employees
    employees = [
        {
            "id": 1,
            "username": "jsmith"
        },
        {
            "id": 2,
            "username": "adoe"
        },
        {
            "id": 3,
            "username": "bwilliams"
        }
    ]

    cases = [
        {
            "id": 1,
            "patientName": "Jane Smith",
            "modality": "CT",
            "studyDate": "2024-11-01",
            "status": "PENDING",
            "report": None,
            "claimedAt": None,
            "claimedBy": None
        },
        {
            "id": 2,
            "patientName": "John Davis",
            "modality": "MRI",
            "studyDate": "2024-11-02",
            "status": "PENDING",
            "report": None,
            "claimedAt": None,
            "claimedBy": None
        },
        {
            "id": 3,
            "patientName": "Sarah Wilson",
            "modality": "XR",
            "studyDate": "2024-11-03",
            "status": "IN_PROGRESS",
            "report": None,
            "claimedAt": "2024-11-03T10:30:00",
            "claimedBy": 1
        },
        {
            "id": 4,
            "patientName": "Michael Brown",
            "modality": "US",
            "studyDate": "2024-11-04",
            "status": "COMPLETED",
            "report": "No acute findings.",
            "claimedAt": "2024-11-04T09:00:00",
            "claimedBy": 2
        },
        {
            "id": 5,
            "patientName": "Emily Johnson",
            "modality": "CT",
            "studyDate": "2024-11-05",
            "status": "PENDING",
            "report": None,
            "claimedAt": None,
            "claimedBy": None
        },
        {
            "id": 6,
            "patientName": "Robert Miller",
            "modality": "MRI",
            "studyDate": "2024-11-06",
            "status": "IN_PROGRESS",
            "report": None,
            "claimedAt": "2024-11-06T14:15:00",
            "claimedBy": 3
        },
        {
            "id": 7,
            "patientName": "Lisa Anderson",
            "modality": "XR",
            "studyDate": "2024-11-07",
            "status": "COMPLETED",
            "report": "Normal chest X-ray.",
            "claimedAt": "2024-11-07T11:00:00",
            "claimedBy": 1
        },
        {
            "id": 8,
            "patientName": "David Thomas",
            "modality": "US",
            "studyDate": "2024-11-08",
            "status": "PENDING",
            "report": None,
            "claimedAt": None,
            "claimedBy": None
        }
    ]

# 1. List Cases
@app.get("/cases")
def get_cases(status=None, claimedBy=None):
    filtered_cases = []

    for case in cases:

        if status is not None:
            if case["status"] != status:
                continue

        if claimedBy is not None:
            employee_id = None
            for employee in employees:
                if employee["username"] == claimedBy:
                    employee_id = employee["id"]
                    break
            if employee_id is None:
                raise HTTPException(status_code=404, detail="No employee found with that username")
            if case["claimedBy"] != employee_id:
                continue

        filtered_cases.append(case)

    filtered_cases.sort(key=lambda case: case["studyDate"])

    return filtered_cases

# 2. Get a Single Case
@app.get("/cases/{id}")
def get_case(id):
    for case in cases:
        if case["id"] == int(id):
            return case

    raise HTTPException(status_code=404, detail="Case not found")


# 3. Manage Employees
@app.get("/employees")
def get_employees():
    return employees


@app.post("/employees")
def create_employee(employee: dict):

    if "username" not in employee:
        raise HTTPException(
            status_code=400,
            detail="Username is required"
        )

    username = employee["username"]

    if username == "":
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty"
        )

    for existing_employee in employees:
        if existing_employee["username"] == username:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )

    global next_employee_id

    new_employee = {
        "id": next_employee_id,
        "username": username
    }

    next_employee_id += 1

    employees.append(new_employee)

    return new_employee


@app.put("/employees/{id}")
def update_employee(id: int, employee: dict):

    if "username" not in employee:
        raise HTTPException(
            status_code=400,
            detail="Username is required"
        )

    username = employee["username"]

    if username == "":
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty"
        )

    for existing_employee in employees:
        if existing_employee["id"] == id:
            for other_employee in employees:
                if other_employee["id"] != id:
                    if other_employee["username"] == username:
                        raise HTTPException(
                            status_code=400,
                            detail="Username already taken"
                        )

            existing_employee["username"] = username

            return existing_employee

    raise HTTPException(
        status_code=404,
        detail="Employee not found"
    )


@app.delete("/employees/{id}")
def delete_employee(id: int):

    for employee in employees:

        if employee["id"] == id:
            employees.remove(employee)
            return employee

    raise HTTPException(
        status_code=404,
        detail="Employee not found"
    )

# 4. Claim a Case
@app.post("/cases/{id}/claim")
def claim_case(id: int, claim_data: dict):
    # Find the case
    case = None
    for existing_case in cases:
        if existing_case["id"] == id:
            case = existing_case
            break

    # Case doesn't exist
    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )
    # Case must be PENDING
    if case["status"] != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Case is not in PENDING status"
        )

    # Check username exists
    if "claimedBy" not in claim_data:
        raise HTTPException(
            status_code=400,
            detail="Username is required"
        )
    username = claim_data["claimedBy"]

    # Find employee
    employee = None

    for existing_employee in employees:
        if existing_employee["username"] == username:
            employee = existing_employee
            break

    # Employee doesn't exist
    if employee is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid username"
        )

    # Claim the case
    case["status"] = "IN_PROGRESS"
    case["claimedAt"] = datetime.now().isoformat()
    case["claimedBy"] = employee["id"]

    return case

# 5. Submit a Report
@app.post("/cases/{id}/report")
def submit_report(id: int, report_data: dict):

    # Find the case
    case = None

    for existing_case in cases:
        if existing_case["id"] == id:
            case = existing_case
            break

    # Case doesn't exist
    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    # Case must be IN_PROGRESS
    if case["status"] != "IN_PROGRESS":
        raise HTTPException(
            status_code=400,
            detail="Case is not in IN_PROGRESS status"
        )

    # Check that author exists
    if "author" not in report_data:
        raise HTTPException(
            status_code=400,
            detail="Username is required"
        )

    username = report_data["author"]

    # Check that report exists
    if "report" not in report_data:
        raise HTTPException(
            status_code=400,
            detail="Report is required"
        )

    report = report_data["report"]

    # Check that report isn't empty
    if report == "":
        raise HTTPException(
            status_code=400,
            detail="Report cannot be empty"
        )

    # Find the employee
    employee = None

    for existing_employee in employees:
        if existing_employee["username"] == username:
            employee = existing_employee
            break

    # Employee doesn't exist
    if employee is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid username"
        )

    # Check that this employee claimed the case
    if case["claimedBy"] != employee["id"]:
        raise HTTPException(
            status_code=400,
            detail="Employee did not claim this case"
        )

    # Save report and complete case
    case["report"] = report
    case["status"] = "COMPLETED"

    return case

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)