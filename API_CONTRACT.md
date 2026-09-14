# ComplianceIQ API Contract

Base URL (local dev): `http://localhost:8000`

All protected routes require a header:
```
Authorization: Bearer <access_token>
```

---

## Auth

### POST `/auth/login`
Login form is **form-urlencoded**, not JSON (OAuth2 standard).

Request (form fields):
```
username = "admin@complianceiq.com"   // yes, "username" holds the email
password = "Admin@1234"
```

Response `200`:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user_id": "uuid",
  "email": "admin@complianceiq.com",
  "role": "admin"
}
```

Default accounts:
| Email | Password | Role |
|---|---|---|
| admin@complianceiq.com | Admin@1234 | admin |
| officer@complianceiq.com | Officer@1234 | officer |
| analyst@complianceiq.com | Analyst@1234 | analyst |

### GET `/auth/me`
Returns the logged-in user's profile.
```json
{ "id": "uuid", "email": "...", "role": "...", "last_login_at": "..." }
```

---

## Transactions

### POST `/transactions/check`
Request:
```json
{
  "sender_account": "ACC10234",
  "receiver_account": "ACC98712",
  "amount": 980000,
  "transaction_type": "transfer",
  "hour_of_day": 2,
  "tx_count_7d": 4,
  "kyc_verified": false
}
```
Response `200`:
```json
{
  "transaction_id": "uuid",
  "flagged": true,
  "risk_level": "HIGH",
  "risk_score": 0.91,
  "violations": [
    { "rule_id": "R002", "rule_name": "Possible Structuring / Smurfing", "regulation_source": "...", "severity": "high" }
  ],
  "shap_explanation": [ { "feature_name": "amount", "display_name": "Transaction Amount", "...": "..." } ],
  "alert_id": "uuid",
  "message": "Transaction flagged and alert created."
}
```

---

## Alerts

### GET `/alerts?status=open&risk_level=high&limit=50&offset=0`
All query params optional.
```json
{
  "total": 5,
  "alerts": [
    {
      "id": "uuid",
      "transaction_id": "uuid",
      "risk_level": "high",
      "violation_type": "...",
      "regulation_cited": "...",
      "status": "open",
      "created_at": "iso-datetime",
      "resolved_at": null
    }
  ]
}
```

### GET `/alerts/{alert_id}`
Full alert detail including SHAP features and the transaction that triggered it.
```json
{
  "id": "uuid",
  "risk_level": "high",
  "violation_type": "...",
  "regulation_cited": "...",
  "ai_explanation": "...",
  "shap_features": "json-string",
  "status": "open",
  "resolution_notes": null,
  "created_at": "iso-datetime",
  "transaction": {
    "id": "uuid", "sender_account": "...", "receiver_account": "...",
    "amount": 980000, "hour_of_day": 2, "tx_count_7d": 4,
    "kyc_verified": false, "risk_score": 0.91
  }
}
```

### PUT `/alerts/{alert_id}/resolve` — officer/admin only
Request: `{ "notes": "Verified with customer." }`
Response: `{ "message": "Alert resolved.", "alert_id": "uuid" }`
Analyst role → `403 Forbidden`

### PUT `/alerts/{alert_id}/escalate` — officer/admin only
Response: `{ "message": "Alert escalated.", "alert_id": "uuid" }`

---

## Dashboard

### GET `/dashboard/summary`
```json
{
  "alerts_today": 2,
  "high_risk_open": 3,
  "resolved_week": 1,
  "total_open": 5,
  "system_status": "operational"
}
```

---

## Admin (admin role only)

### POST `/users`
Request: `{ "email": "...", "password": "...", "role": "analyst" }`
Response: `{ "message": "User created.", "user_id": "uuid", "email": "...", "role": "..." }`

### GET `/users`
Returns array of all users.

### PUT `/users/{user_id}/deactivate`
Response: `{ "message": "User ... deactivated." }`

### GET `/audit-logs?limit=100&action_filter=login_success`
Returns array of audit log entries.

---

## Chatbot

### POST `/chatbot/ask`
Request: `{ "question": "..." }`
Response (placeholder until Part B RAG is wired in):
```json
{ "question": "...", "answer": "Chatbot will be active after the RAG pipeline is integrated...", "sources": [] }
```

---

## Errors

| Code | Meaning |
|---|---|
| 401 | Missing/invalid/expired token, or wrong login credentials |
| 403 | Logged in but role not permitted for this route |
| 404 | Resource not found |
| 422 | Request body doesn't match expected shape |
| 429 | Account locked (5 failed logins → 15 min lockout) |

---

*Generated from the actual tested routes in `app/main.py` as of the Part A completion milestone (all 20 automated tests passing).*
