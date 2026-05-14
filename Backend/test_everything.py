# ============================================================
# FILE: backend/test_everything.py
# ============================================================
#
# WHAT IS THIS FILE?
# ------------------
# This script tests every single API endpoint automatically.
# Run it to verify your entire backend is working correctly
# before handing off to Person 3.
#
# HOW TO RUN:
# -----------
# Make sure the server IS running in another terminal:
#     uvicorn app.main:app --reload
#
# Then in a NEW terminal (with .venv active), from backend/ folder:
#     python test_everything.py
#
# You should see:
#     Running ComplianceIQ Backend Tests...
#     ✓ Health check
#     ✓ Login as admin
#     ✓ Login as officer
#     ✓ Login as analyst
#     ✓ Get my profile
#     ✓ Dashboard summary
#     ✓ Submit flagged transaction
#     ✓ Submit clean transaction
#     ✓ Get all alerts
#     ✓ Get single alert
#     ✓ Resolve alert as officer
#     ✓ Analyst cannot resolve (403 expected)
#     ✓ Create user
#     ✓ List users
#     ✓ Get audit logs
#     ✓ Chatbot placeholder
#
#     ALL 16 TESTS PASSED ✓
#
# If any test shows ✗, the error message tells you what's wrong.
# ============================================================

import requests
import json
import sys

BASE = "http://localhost:8000"

# Colours for terminal output
GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"

passed = 0
failed = 0

def test(name, condition, error_msg=""):
    global passed, failed
    if condition:
        print(f"  {GREEN}✓{RESET} {name}")
        passed += 1
    else:
        print(f"  {RED}✗ {name}{RESET}")
        if error_msg:
            print(f"    → {error_msg}")
        failed += 1

def get_token(email, password):
    """Log in and return the access token."""
    r = requests.post(f"{BASE}/auth/login", data={"username": email, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

def headers(token):
    """Return auth headers dict."""
    return {"Authorization": f"Bearer {token}"}

print()
print("Running ComplianceIQ Backend Tests...")
print("=" * 45)

# ── TEST 1: Health check ─────────────────────────────────────────────────────
r = requests.get(f"{BASE}/")
test("Health check", r.status_code == 200 and r.json()["status"] == "running",
     f"Got {r.status_code}: {r.text[:100]}")

# ── TEST 2-4: Login ──────────────────────────────────────────────────────────
admin_token = get_token("admin@complianceiq.com", "Admin@1234")
test("Login as admin", admin_token is not None,
     "Login failed — check the server is running and default users exist")

officer_token = get_token("officer@complianceiq.com", "Officer@1234")
test("Login as officer", officer_token is not None)

analyst_token = get_token("analyst@complianceiq.com", "Analyst@1234")
test("Login as analyst", analyst_token is not None)

if not admin_token:
    print()
    print(f"{RED}Cannot continue — admin login failed.{RESET}")
    print("Make sure the server is running: uvicorn app.main:app --reload")
    sys.exit(1)

# ── TEST 5: Get my profile ──────────────────────────────────────────────────
r = requests.get(f"{BASE}/auth/me", headers=headers(admin_token))
test("Get my profile",
     r.status_code == 200 and r.json()["role"] == "admin",
     f"Got {r.status_code}: {r.text[:100]}")

# ── TEST 6: Dashboard summary ────────────────────────────────────────────────
r = requests.get(f"{BASE}/dashboard/summary", headers=headers(officer_token))
data = r.json()
test("Dashboard summary",
     r.status_code == 200 and "alerts_today" in data and "total_open" in data,
     f"Got {r.status_code}: {r.text[:100]}")

# ── TEST 7: Submit a HIGH RISK flagged transaction ───────────────────────────
r = requests.post(f"{BASE}/transactions/check",
    headers=headers(officer_token),
    json={
        "sender_account": "TEST001",
        "receiver_account": "TEST002",
        "amount": 980000,
        "transaction_type": "transfer",
        "hour_of_day": 2,
        "tx_count_7d": 4,
        "kyc_verified": False,
    }
)
tx_data = r.json()
test("Submit flagged transaction",
     r.status_code == 200 and tx_data.get("flagged") == True and tx_data.get("risk_level") == "high",
     f"Got {r.status_code}: {r.text[:200]}")

flagged_alert_id = tx_data.get("alert_id")

# ── TEST 8: Submit a CLEAN transaction ───────────────────────────────────────
r = requests.post(f"{BASE}/transactions/check",
    headers=headers(officer_token),
    json={
        "sender_account": "TEST003",
        "receiver_account": "TEST004",
        "amount": 25000,
        "transaction_type": "transfer",
        "hour_of_day": 14,
        "tx_count_7d": 1,
        "kyc_verified": True,
    }
)
clean_data = r.json()
test("Submit clean transaction",
     r.status_code == 200 and clean_data.get("flagged") == False,
     f"Got {r.status_code}: {r.text[:200]}")

# ── TEST 9: Get all alerts ───────────────────────────────────────────────────
r = requests.get(f"{BASE}/alerts", headers=headers(analyst_token))
alerts_data = r.json()
test("Get all alerts",
     r.status_code == 200 and "alerts" in alerts_data and "total" in alerts_data,
     f"Got {r.status_code}: {r.text[:200]}")

# ── TEST 10: Get all alerts filtered by status ───────────────────────────────
r = requests.get(f"{BASE}/alerts?status=open", headers=headers(analyst_token))
test("Get alerts filtered by status=open",
     r.status_code == 200 and "alerts" in r.json(),
     f"Got {r.status_code}: {r.text[:200]}")

# ── TEST 11: Get single alert ────────────────────────────────────────────────
if flagged_alert_id:
    r = requests.get(f"{BASE}/alerts/{flagged_alert_id}", headers=headers(analyst_token))
    alert_detail = r.json()
    test("Get single alert detail",
         r.status_code == 200 and "ai_explanation" in alert_detail and "transaction" in alert_detail,
         f"Got {r.status_code}: {r.text[:200]}")
else:
    test("Get single alert detail", False, "No alert_id from previous test")

# ── TEST 12: Officer can resolve an alert ────────────────────────────────────
if flagged_alert_id:
    r = requests.put(f"{BASE}/alerts/{flagged_alert_id}/resolve",
        headers=headers(officer_token),
        json={"notes": "Test resolution from automated test."}
    )
    test("Officer resolves alert",
         r.status_code == 200 and "resolved" in r.json().get("message",""),
         f"Got {r.status_code}: {r.text[:200]}")
else:
    test("Officer resolves alert", False, "No alert_id")

# ── TEST 13: Analyst CANNOT resolve (should get 403) ────────────────────────
if flagged_alert_id:
    # Create a new alert to try resolving as analyst
    r2 = requests.post(f"{BASE}/transactions/check",
        headers=headers(officer_token),
        json={"sender_account": "X1", "receiver_account": "X2",
              "amount": 960000, "hour_of_day": 1, "tx_count_7d": 3, "kyc_verified": False}
    )
    new_alert_id = r2.json().get("alert_id")
    if new_alert_id:
        r = requests.put(f"{BASE}/alerts/{new_alert_id}/resolve",
            headers=headers(analyst_token),
            json={"notes": "Analyst trying to resolve"}
        )
        test("Analyst cannot resolve (expects 403)",
             r.status_code == 403,
             f"Expected 403, got {r.status_code}: {r.text[:100]}")
    else:
        test("Analyst cannot resolve (expects 403)", False, "Couldn't create test alert")
else:
    test("Analyst cannot resolve (expects 403)", False, "No alert_id")

# ── TEST 14: Admin creates a new user ────────────────────────────────────────
import time
test_email = f"testuser_{int(time.time())}@test.com"
r = requests.post(f"{BASE}/users",
    headers=headers(admin_token),
    json={"email": test_email, "password": "Test@1234", "role": "analyst"}
)
test("Admin creates user",
     r.status_code == 201 and r.json().get("email") == test_email,
     f"Got {r.status_code}: {r.text[:200]}")

# ── TEST 15: Admin lists all users ───────────────────────────────────────────
r = requests.get(f"{BASE}/users", headers=headers(admin_token))
test("Admin lists users",
     r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) > 0,
     f"Got {r.status_code}: {r.text[:200]}")

# ── TEST 16: Admin views audit logs ─────────────────────────────────────────
r = requests.get(f"{BASE}/audit-logs", headers=headers(admin_token))
test("Get audit logs",
     r.status_code == 200 and isinstance(r.json(), list),
     f"Got {r.status_code}: {r.text[:200]}")

# ── TEST 17: Analyst cannot view audit logs (403) ────────────────────────────
r = requests.get(f"{BASE}/audit-logs", headers=headers(analyst_token))
test("Analyst cannot view audit logs (expects 403)",
     r.status_code == 403,
     f"Expected 403, got {r.status_code}")

# ── TEST 18: Chatbot placeholder ─────────────────────────────────────────────
r = requests.post(f"{BASE}/chatbot/ask",
    headers=headers(analyst_token),
    json={"question": "What is the KYC rule for transfers above 10 lakh?"}
)
test("Chatbot placeholder works",
     r.status_code == 200 and "question" in r.json() and "answer" in r.json(),
     f"Got {r.status_code}: {r.text[:200]}")

# ── TEST 19: Unauthenticated request gets 401 ────────────────────────────────
r = requests.get(f"{BASE}/alerts")  # no token
test("No token → 401 Unauthorized",
     r.status_code == 401,
     f"Expected 401, got {r.status_code}")

# ── TEST 20: Invalid token gets 401 ─────────────────────────────────────────
r = requests.get(f"{BASE}/alerts", headers={"Authorization": "Bearer fakeinvalidtoken"})
test("Fake token → 401 Unauthorized",
     r.status_code == 401,
     f"Expected 401, got {r.status_code}")

# ── SUMMARY ──────────────────────────────────────────────────────────────────
print()
print("=" * 45)
total = passed + failed
if failed == 0:
    print(f"{GREEN}ALL {total} TESTS PASSED ✓{RESET}")
    print()
    print("Your backend is working correctly.")
    print("Share API_CONTRACT.md with Person 3 now.")
else:
    print(f"{RED}{failed} TEST(S) FAILED ✗{RESET}  ({passed}/{total} passed)")
    print()
    print("Fix the failing tests before sharing with Person 3.")
print("=" * 45)
print()
