import requests

API_KEY = 'NOKEY'  # ← replace with your key
HEADERS = {
    'Authorization': API_KEY,
    'Content-Type': 'application/json'
}

# 1) Fetch department_id
d = requests.get('https://api.manifest.ly/api/v1/departments', headers=HEADERS)
d.raise_for_status()
dept_id = d.json()['departments'][0]['id']
print("Using department_id =", dept_id)

# 2) Create workflow with header steps
create_url = f'https://api.manifest.ly/api/v1/checklists?department_id={dept_id}'
headers = HEADERS
payload = {
    "business_days": [],
    "description": "Full CK Lens Onboarding Workflow",
    "expected_duration": 7,
    "expected_duration_units": "days",   # must be "days" or "hours" :contentReference[oaicite:0]{index=0}
    "external_id": "cklens-onboarding-001",
    "hide_steps_from_external": False,
    "tag_list": "",                      # omit or a simple string
    "title": "CK Lens Customer Onboarding",
    "steps": [
        {"title": "Identify Customer Type",                "header_step": True},
        {"title": "Send Onboarding Email",                 "header_step": True},
        {"title": "Await Customer Response",               "header_step": True},
        {"title": "Verify Documents Received",             "header_step": True},
        {"title": "CK Lens Platform Testing",              "header_step": True},
        {"title": "Verify Data Availability",              "header_step": True},
        {"title": "CK Lens Basic Setup",                   "header_step": True},
        {"title": "Share CK Lens Credentials",             "header_step": True},
        {"title": "Schedule CK Lens Walkthrough",          "header_step": True},
        {"title": "Conduct Walkthrough / Close Onboarding","header_step": True}
    ]
}

resp = requests.post(create_url, headers=headers, json=payload)
resp.raise_for_status()
workflow = resp.json()['checklist']
checklist_id = workflow['id']
print(f"Workflow created: ID = {checklist_id}")

# 3) Fetch full details to get header step IDs
details_url = f'https://api.manifest.ly/api/v1/checklists/{checklist_id}'
details = requests.get(details_url, headers=headers).json()['checklist']  # full steps list :contentReference[oaicite:1]{index=1}

parent_ids = { s['title']: s['id'] for s in details['steps'] }

# 4) Define and add all child steps
child_steps_map = {
    "Identify Customer Type": [
        "Indian Customer",
        "Non-Indian Customer"
    ],
    "Send Onboarding Email": [
        "Customer Name",
        "Customer Email Address(es)",
        "Additional CC Addresses",
        "Subject: [Customer Name] | Customer Onboarding form for Invoice Processing",
        "Body Template: Non-Indian",
        "Body Template: Indian"
    ],
    "Await Customer Response": [
        "Wait for completed form and all requested documents"
    ],
    "Verify Documents Received": [
        "Onboarding form completed",
        "Company Registration/COI",
        "Monthly invoice recipients (To & Cc emails)",
        "GST Certificate (Indian customers only)",
        "Company PAN (Indian customers only)"
    ],
    "CK Lens Platform Testing": [
        "Load customer data into Virtuso",
        "Follow Virtuso testing steps",
        "Confirm data flows into CK Lens"
    ],
    "Verify Data Availability": [
        "≥ 3 days of billing data visible in CK Lens",
        "Data export works correctly",
        "Filters and dashboards function as expected"
    ],
    "CK Lens Basic Setup": [
        "Validate discounts, private pricing & initial credits against agreement sheet",
        "Export sample reports & confirm filters",
        "Create users (from FinOps sheet contact info)",
        "Create notification groups",
        "Apply alerts: Billing Summary, RI Expiry, RI Utilization"
    ],
    "Share CK Lens Credentials": [
        "Email subject: CK Lens Account Setup Complete",
        "Email body & attachment: overview, instructions & Quick-Start Guide"
    ],
    "Schedule CK Lens Walkthrough": [
        "Request 2–3 available time slots",
        "Follow up up to 3 times if no response",
        "If customer declines or unavailable → skip to Step 10"
    ],
    "Conduct Walkthrough / Close Onboarding": [
        "If call scheduled: Host the walkthrough",
        "Send MoM (support path, tuner guide, filters, cost explanation)",
        "If no call: Send MoM summary email",
        "Mark onboarding as complete"
    ]
}

steps_url = f'https://api.manifest.ly/api/v1/checklists/{checklist_id}/steps'
for header_title, children in child_steps_map.items():
    parent_id = parent_ids[header_title]
    for child in children:
        step_payload = {
            "title": child,
            "header_step": False,
            "parent_step_id": parent_id
        }
        r = requests.post(steps_url, headers=headers, json=step_payload)
        if r.status_code == 201:
            print(f"✓ Added under '{header_title}': {child}")
        else:
            print(f"✗ Failed to add '{child}':", r.status_code, r.text)
