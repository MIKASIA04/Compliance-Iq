export const dashboardStats = {

  alerts_today: 24,

  high_risk_open: 8,

  resolved_week: 41,
};

export const mockAlerts = [

  {
    id: 1,

    transaction_id: "TXN-48291",

    amount: 85000,

    risk_level: "high",

    risk_score: 94,

    status: "open",

    created_at: "14 May 2026 • 10:24 AM",

    ai_explanation:
      "Large cross-border transaction flagged due to unusual transfer pattern and high-risk jurisdiction.",

    shap_explanation: [
      {
        feature: "Transaction Amount",
        impact: 92,
      },

      {
        feature: "Country Risk",
        impact: 81,
      },

      {
        feature: "Frequency Spike",
        impact: 65,
      },

      {
        feature: "New Beneficiary",
        impact: 48,
      },
    ],
  },

  {
    id: 2,

    transaction_id: "TXN-59312",

    amount: 32000,

    risk_level: "medium",

    risk_score: 67,

    status: "open",

    created_at: "14 May 2026 • 09:15 AM",

    ai_explanation:
      "Transaction velocity increased significantly compared to normal customer behavior.",

    shap_explanation: [
      {
        feature: "Velocity",
        impact: 74,
      },

      {
        feature: "Account Age",
        impact: 52,
      },

      {
        feature: "Geolocation Mismatch",
        impact: 44,
      },
    ],
  },

  {
    id: 3,

    transaction_id: "TXN-71244",

    amount: 120000,

    risk_level: "high",

    risk_score: 97,

    status: "resolved",

    created_at: "13 May 2026 • 06:42 PM",

    ai_explanation:
      "Multiple linked transactions detected across newly added offshore beneficiaries.",

    shap_explanation: [
      {
        feature: "Offshore Routing",
        impact: 95,
      },

      {
        feature: "Beneficiary Risk",
        impact: 88,
      },

      {
        feature: "Amount Spike",
        impact: 71,
      },
    ],
  },

  {
    id: 4,

    transaction_id: "TXN-88103",

    amount: 14500,

    risk_level: "low",

    risk_score: 28,

    status: "resolved",

    created_at: "13 May 2026 • 01:08 PM",

    ai_explanation:
      "Minor anomaly detected but transaction aligns with historical customer behavior.",

    shap_explanation: [
      {
        feature: "Behavior Consistency",
        impact: 22,
      },

      {
        feature: "Location Match",
        impact: 14,
      },
    ],
  },

  {
    id: 5,

    transaction_id: "TXN-91027",

    amount: 67000,

    risk_level: "medium",

    risk_score: 73,

    status: "open",

    created_at: "12 May 2026 • 08:37 PM",

    ai_explanation:
      "AI model identified suspicious transaction timing combined with elevated transfer value.",

    shap_explanation: [
      {
        feature: "Transfer Timing",
        impact: 68,
      },

      {
        feature: "Amount Deviation",
        impact: 77,
      },

      {
        feature: "Recipient History",
        impact: 49,
      },
    ],
  },
];