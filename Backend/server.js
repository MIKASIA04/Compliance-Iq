import express from "express";
import cors from "cors";

const app = express();

app.use(cors());
app.use(express.json());

/* ALERTS API */

app.get("/alerts", (req, res) => {

  res.json([

    {
      id: 1,

      transaction_id: "TXN-92841",

      amount: 125000,

      risk_level: "high",

      status: "under review",

      created_at: "14 May 2026",

      risk_score: 92,

      ai_explanation:
        "Large transaction flagged due to unusual transfer frequency.",

      shap_explanation: [

        {
          feature: "Transaction Amount",
          impact: 92,
        },

        {
          feature: "Transfer Frequency",
          impact: 74,
        },

        {
          feature: "Location Risk",
          impact: 58,
        },

      ],
    },

    {
      id: 2,

      transaction_id: "TXN-92842",

      amount: 42000,

      risk_level: "medium",

      status: "pending",

      created_at: "14 May 2026",

      risk_score: 68,

      ai_explanation:
        "Cross-border transfer pattern detected.",

      shap_explanation: [

        {
          feature: "Cross Border Activity",
          impact: 70,
        },

        {
          feature: "Transaction Velocity",
          impact: 52,
        },

        {
          feature: "Risk Geography",
          impact: 48,
        },

      ],
    },

    {
      id: 3,

      transaction_id: "TXN-92843",

      amount: 15000,

      risk_level: "low",

      status: "resolved",

      created_at: "13 May 2026",

      risk_score: 28,

      ai_explanation:
        "Low anomaly score with regular transaction behavior.",

      shap_explanation: [

        {
          feature: "Stable Account History",
          impact: 30,
        },

        {
          feature: "Low Transaction Volume",
          impact: 22,
        },

        {
          feature: "Trusted Region",
          impact: 18,
        },

      ],
    },

  ]);

});
app.patch("/alerts/:id/resolve", (req, res) => {

  res.json({
    success: true,
    message: "Alert resolved",
  });

});

app.patch("/alerts/:id/escalate", (req, res) => {

  res.json({
    success: true,
    message: "Alert escalated",
  });

});

/* DASHBOARD STATS API */

app.get("/dashboard-stats", (req, res) => {

  res.json({

    alerts_today: 20,

    high_risk_open: 7,

    resolved_week: 18,

  });

});

const PORT = 5000;

app.listen(PORT, () => {

  console.log(
    `Server running on port ${PORT}`
  );

});