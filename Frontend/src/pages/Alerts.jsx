import { useState } from "react";

import Layout from "../components/Layout";

import { mockAlerts } from "../api/mockData";

import {
  ChevronDown,
  ChevronUp,
} from "lucide-react";

import toast from "react-hot-toast";

import useAuth from "../hooks/useAuth";

export default function Alerts() {

  const { getRole } = useAuth();

  const role = getRole();

  /* ALERT STATE */

  const [alerts, setAlerts] =
    useState(mockAlerts);

  const [selectedRisk, setSelectedRisk] =
    useState("all");

  const [search, setSearch] =
    useState("");

  const [expandedAlert, setExpandedAlert] =
    useState(null);

  /* FILTERING */

  const filteredAlerts = alerts.filter(
    (alert) => {

      const matchesRisk =
        selectedRisk === "all"
          ? true
          : alert.risk_level === selectedRisk;

      const matchesSearch =
        alert.transaction_id
          .toLowerCase()
          .includes(
            search.toLowerCase()
          );

      return (
        matchesRisk &&
        matchesSearch
      );
    }
  );

  /* LIVE STATS */

  const totalAlerts =
    alerts.length;

  const highRisk =
    alerts.filter(
      (a) => a.risk_level === "high"
    ).length;

  const resolved =
    alerts.filter(
      (a) => a.status === "resolved"
    ).length;

  const underReview =
    alerts.filter(
      (a) => a.status === "under review"
    ).length;

  /* ACTIONS */

  function resolveAlert(id) {

    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === id
          ? {
              ...alert,
              status: "resolved",
              risk_level: "low",
            }
          : alert
      )
    );

    toast.success(
      "Alert resolved successfully"
    );
  }

  function escalateAlert(id) {

    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === id
          ? {
              ...alert,
              status: "under review",
              risk_level: "high",
            }
          : alert
      )
    );

    toast.error(
      "Alert escalated for enhanced review"
    );
  }

  return (
    <Layout>

      <div>

        {/* HEADER */}

        <div>

          <h1
            className="
              text-3xl
              font-bold

              text-slate-900
              dark:text-white
            "
          >
            Alerts Management
          </h1>

          <p
            className="
              mt-2

              text-slate-500
              dark:text-slate-400
            "
          >
            Monitor and investigate suspicious transactions
          </p>

        </div>

        {/* LIVE STATS */}

        <div
          className="
            grid
            grid-cols-1
            md:grid-cols-4

            gap-5

            mt-6
          "
        >

          {/* TOTAL */}

          <div
            className="
              bg-white
              dark:bg-slate-900

              border
              border-slate-200
              dark:border-slate-800

              rounded-2xl

              p-4

              shadow-sm
            "
          >

            <p
              className="
                text-sm

                text-slate-500
                dark:text-slate-400
              "
            >
              Total Alerts
            </p>

            <h2
              className="
                text-2xl
                font-bold

                mt-2

                text-slate-900
                dark:text-white
              "
            >
              {totalAlerts}
            </h2>

          </div>

          {/* HIGH RISK */}

          <div
            className="
              bg-white
              dark:bg-slate-900

              border
              border-slate-200
              dark:border-slate-800

              rounded-2xl

              p-4

              shadow-sm
            "
          >

            <p
              className="
                text-sm

                text-slate-500
                dark:text-slate-400
              "
            >
              High Risk
            </p>

            <h2
              className="
                text-2xl
                font-bold

                mt-2

                text-red-500
              "
            >
              {highRisk}
            </h2>

          </div>

          {/* RESOLVED */}

          <div
            className="
              bg-white
              dark:bg-slate-900

              border
              border-slate-200
              dark:border-slate-800

              rounded-2xl

              p-4

              shadow-sm
            "
          >

            <p
              className="
                text-sm

                text-slate-500
                dark:text-slate-400
              "
            >
              Resolved
            </p>

            <h2
              className="
                text-2xl
                font-bold

                mt-2

                text-green-500
              "
            >
              {resolved}
            </h2>

          </div>

          {/* UNDER REVIEW */}

          <div
            className="
              bg-white
              dark:bg-slate-900

              border
              border-slate-200
              dark:border-slate-800

              rounded-2xl

              p-4

              shadow-sm
            "
          >

            <p
              className="
                text-sm

                text-slate-500
                dark:text-slate-400
              "
            >
              Under Review
            </p>

            <h2
              className="
                text-2xl
                font-bold

                mt-2

                text-amber-500
              "
            >
              {underReview}
            </h2>

          </div>

        </div>

        {/* TABLE */}

        <div
          className="
            mt-8

            bg-white
            dark:bg-slate-900

            border
            border-slate-200
            dark:border-slate-800

            rounded-2xl

            shadow-sm

            overflow-hidden
          "
        >

          {/* TOOLBAR */}

          <div
            className="
              flex
              flex-col
              lg:flex-row

              lg:items-center
              lg:justify-between

              gap-4

              p-5

              border-b
              border-slate-200
              dark:border-slate-800
            "
          >

            {/* SEARCH */}

            <input
              type="text"

              placeholder="Search transaction ID..."

              value={search}

              onChange={(e) =>
                setSearch(e.target.value)
              }

              className="
                w-full
                lg:w-80

                px-4
                py-3

                rounded-xl

                border
                border-slate-300
                dark:border-slate-700

                bg-white
                dark:bg-slate-800

                text-slate-900
                dark:text-white

                outline-none

                focus:ring-2
                focus:ring-blue-500/20
              "
            />

            {/* FILTERS */}

            <div className="flex gap-3">

              {[
                "all",
                "high",
                "medium",
                "low",
              ].map((risk) => (

                <button
                  key={risk}

                  onClick={() =>
                    setSelectedRisk(risk)
                  }

                  className={`
                    px-4
                    py-2

                    rounded-xl

                    text-sm
                    font-medium

                    transition-all

                    ${
                      selectedRisk === risk
                        ? "bg-slate-900 text-white"
                        : `
                          bg-slate-100
                          dark:bg-slate-800

                          text-slate-700
                          dark:text-slate-300
                        `
                    }
                  `}
                >

                  {risk.charAt(0).toUpperCase() +
                    risk.slice(1)}

                </button>

              ))}

            </div>

          </div>

          {/* TABLE */}

          <div className="overflow-x-auto">

            <table className="w-full min-w-[950px]">

              <thead
                className="
                  bg-slate-50
                  dark:bg-slate-800
                "
              >

                <tr
                  className="
                    text-left
                    text-sm

                    text-slate-500
                    dark:text-slate-300
                  "
                >

                  <th className="px-6 py-4 font-medium">
                    Transaction ID
                  </th>

                  <th className="px-6 py-4 font-medium">
                    Amount
                  </th>

                  <th className="px-6 py-4 font-medium">
                    Risk
                  </th>

                  <th className="px-6 py-4 font-medium">
                    Status
                  </th>

                  <th className="px-6 py-4 font-medium">
                    Created
                  </th>

                  <th className="px-6 py-4 font-medium">
                    Expand
                  </th>

                </tr>

              </thead>

              <tbody>

                {filteredAlerts.map(
                  (alert) => {

                    const isExpanded =
                      expandedAlert === alert.id;

                    return (

                      <tr
                        key={alert.id}
                      >

                        <td colSpan="6" className="p-0">

                          {/* MAIN ROW */}

                          <div
                            onClick={() =>
                              setExpandedAlert(
                                isExpanded
                                  ? null
                                  : alert.id
                              )
                            }

                            className="
                              grid
                              grid-cols-6

                              items-center

                              border-t
                              border-slate-100
                              dark:border-slate-800

                              hover:bg-slate-50
                              dark:hover:bg-slate-800/50

                              transition-all

                              cursor-pointer
                            "
                          >

                            <div className="px-6 py-5 font-medium text-slate-900 dark:text-white">
                              {alert.transaction_id}
                            </div>

                            <div className="px-6 py-5 text-slate-700 dark:text-slate-300">
                              ₹{alert.amount.toLocaleString()}
                            </div>

                            <div className="px-6 py-5">

                              <span
                                className={`
                                  px-3
                                  py-1

                                  rounded-full

                                  text-xs
                                  font-semibold

                                  ${
                                    alert.risk_level ===
                                    "high"
                                      ? `
                                        bg-red-100
                                        text-red-600
                                      `
                                      : `
                                        bg-green-100
                                        text-green-600
                                      `
                                  }
                                `}
                              >

                                {alert.risk_level}

                              </span>

                            </div>

                            <div className="px-6 py-5">

                              <span
                                className={`
                                  px-3
                                  py-1

                                  rounded-full

                                  text-xs
                                  font-medium

                                  ${
                                    alert.status === "resolved"
                                      ? `
                                        bg-green-100
                                        text-green-600
                                      `
                                      : alert.status ===
                                        "under review"
                                      ? `
                                        bg-red-100
                                        text-red-600
                                      `
                                      : `
                                        bg-amber-100
                                        text-amber-600
                                      `
                                  }
                                `}
                              >

                                {alert.status}

                              </span>

                            </div>

                            <div className="px-6 py-5 whitespace-nowrap text-slate-500 dark:text-slate-400">
                              {alert.created_at}
                            </div>

                            <div className="px-6 py-5">

                              {isExpanded ? (
                                <ChevronUp size={18} />
                              ) : (
                                <ChevronDown size={18} />
                              )}

                            </div>

                          </div>

                          {/* EXPANDED PANEL */}

                          {isExpanded && (

                            <div
                              className="
                                px-6
                                py-6

                                bg-slate-50
                                dark:bg-slate-800/50

                                border-t
                                border-slate-100
                                dark:border-slate-700
                              "
                            >

                              <div
                                className="
                                  grid
                                  md:grid-cols-2

                                  gap-6
                                "
                              >

                                {/* AI */}

                                <div>

                                  <h3
                                    className="
                                      text-sm
                                      font-semibold

                                      text-slate-900
                                      dark:text-white

                                      mb-2
                                    "
                                  >
                                    AI Explanation
                                  </h3>

                                  <p
                                    className="
                                      text-sm

                                      leading-6

                                      text-slate-600
                                      dark:text-slate-300
                                    "
                                  >
                                    {alert.ai_explanation}
                                  </p>

                                </div>

                                {/* META */}

                                <div>

                                  <h3
                                    className="
                                      text-sm
                                      font-semibold

                                      text-slate-900
                                      dark:text-white

                                      mb-2
                                    "
                                  >
                                    Investigation Metadata
                                  </h3>

                                  <div
                                    className="
                                      space-y-3

                                      text-sm

                                      text-slate-600
                                      dark:text-slate-300
                                    "
                                  >

                                    <p>
                                      <span className="font-medium">
                                        Risk Score:
                                      </span>{" "}
                                      {alert.risk_score}
                                    </p>

                                    <p>
                                      <span className="font-medium">
                                        AML Flag:
                                      </span>{" "}
                                      Suspicious transaction pattern detected
                                    </p>

                                    <p>
                                      <span className="font-medium">
                                        Suggested Action:
                                      </span>{" "}
                                      Escalate to compliance review
                                    </p>

                                  </div>

                                </div>

                              </div>

                              {/* ACTIONS */}

                              <div className="mt-6 flex flex-wrap gap-3">

                                {role === "admin" && (

                                  <div
                                    className="
                                      px-4
                                      py-2

                                      rounded-xl

                                      bg-slate-100
                                      dark:bg-slate-700

                                      text-slate-600
                                      dark:text-slate-300

                                      text-sm
                                      font-medium
                                    "
                                  >
                                    Admin Oversight Access
                                  </div>

                                )}

                                {role === "analyst" && (

                                  <button
                                    onClick={() =>
                                      toast.success(
                                        "Investigation workflow opened"
                                      )
                                    }
                                    className="
                                      px-4
                                      py-2

                                      rounded-xl

                                      bg-blue-600
                                      hover:bg-blue-700

                                      text-white
                                      text-sm
                                      font-medium
                                    "
                                  >
                                    Investigate Alert
                                  </button>

                                )}

                                {role === "officer" && (

                                  <>
                                    <button
                                      onClick={() =>
                                        resolveAlert(alert.id)
                                      }
                                      className="
                                        px-4
                                        py-2

                                        rounded-xl

                                        bg-green-600
                                        hover:bg-green-700

                                        text-white
                                        text-sm
                                        font-medium
                                      "
                                    >
                                      Resolve Alert
                                    </button>

                                    <button
                                      onClick={() =>
                                        escalateAlert(alert.id)
                                      }
                                      className="
                                        px-4
                                        py-2

                                        rounded-xl

                                        bg-red-600
                                        hover:bg-red-700

                                        text-white
                                        text-sm
                                        font-medium
                                      "
                                    >
                                      Escalate Alert
                                    </button>

                                  </>

                                )}

                              </div>

                            </div>

                          )}

                        </td>

                      </tr>

                    );
                  }
                )}

              </tbody>

            </table>

          </div>

        </div>

      </div>

    </Layout>
  );
}