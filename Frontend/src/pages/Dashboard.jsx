import {
  useEffect,
  useState,
} from "react";

import Layout from "../components/Layout";

import StatCard from "../components/StatCard";
import AlertRow from "../components/AlertRow";
import ShapChart from "../components/ShapChart";


import {
  getDashboardStats,
  getAlerts,
}
from "../api/client";



export default function Dashboard() {

  const [loading, setLoading] =
    useState(true);
    const [dashboardStats, setDashboardStats] =
  useState(null);

const [alerts, setAlerts] =
  useState([]);

  useEffect(() => {

    const timer = setTimeout(() => {

      setLoading(false);

    }, 1800);

    return () => clearTimeout(timer);

  }, []);
  useEffect(() => {

  async function fetchData() {

    try {

      const stats =
        await getDashboardStats();

      const alertsData =
        await getAlerts();

      setDashboardStats(stats);

      setAlerts(alertsData);

    } catch (error) {

      console.error(error);

    }

  }

  fetchData();

}, []);

  if (loading) {

    return (
      <Layout>

        <div className="space-y-8">

          {/* HEADER SKELETON */}

          <div className="space-y-3">

            <div
              className="
                h-8
                w-72

                rounded-xl

                bg-slate-200
                dark:bg-slate-800

                animate-pulse
              "
            />

            <div
              className="
                h-4
                w-96

                rounded-xl

                bg-slate-200
                dark:bg-slate-800

                animate-pulse
              "
            />

          </div>

          {/* STAT CARDS */}

          <div
            className="
              grid
              grid-cols-1
              md:grid-cols-2
              xl:grid-cols-4

              gap-6
            "
          >

            {[1, 2, 3, 4].map((item) => (

              <div
                key={item}
                className="
                  h-32

                  rounded-2xl

                  bg-slate-200
                  dark:bg-slate-800

                  animate-pulse
                "
              />

            ))}

          </div>

          {/* TABLE */}

          <div
            className="
              h-96

              rounded-2xl

              bg-slate-200
              dark:bg-slate-800

              animate-pulse
            "
          />

          {/* CHART */}

          <div
            className="
              h-80

              rounded-2xl

              bg-slate-200
              dark:bg-slate-800

              animate-pulse
            "
          />

        </div>

      </Layout>
    );
  }

  return (
    <Layout>

      <div>

        {/* HEADER */}

        <div>

          <h1
            className="
              text-2xl
              md:text-3xl

              font-semibold

              text-slate-900
              dark:text-white
            "
          >
            Dashboard Overview
          </h1>

          <p
            className="
              text-slate-500
              dark:text-slate-400

              mt-2
            "
          >
            Monitor compliance activity in real time
          </p>

        </div>

        {/* STAT CARDS */}

        <div
          className="
            grid
            grid-cols-1
            md:grid-cols-2
            xl:grid-cols-4

            gap-6
            mt-8
          "
        >

          <StatCard
            title="Alerts Today"
            value={dashboardStats.alerts_today}
            borderColor="border-red-500"
          />

          <StatCard
            title="High Risk Open"
            value={dashboardStats.high_risk_open}
            borderColor="border-amber-500"
          />

          <StatCard
            title="Resolved This Week"
            value={dashboardStats.resolved_week}
            borderColor="border-green-500"
          />

          <StatCard
            title="System Status"
            value="Operational"
            borderColor="border-blue-500"
          />

        </div>

        {/* RECENT ALERTS */}

        <div
          className="
            bg-white
            dark:bg-slate-900

            rounded-2xl

            border
            border-slate-200
            dark:border-slate-800

            shadow-sm

            overflow-hidden

            mt-12

            transition-all
          "
        >

          <div
            className="
              px-6
              py-5

              border-b
              border-slate-100
              dark:border-slate-800
            "
          >

            <h2
              className="
                text-lg
                font-semibold

                text-slate-900
                dark:text-white
              "
            >
              Recent Alerts
            </h2>

            <p
              className="
                text-sm

                text-slate-500
                dark:text-slate-400

                mt-1
              "
            >
              Latest suspicious transactions detected by AI
            </p>

          </div>

          {/* RESPONSIVE TABLE */}

          <div className="overflow-x-auto">

            <table className="w-full min-w-[900px]">

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
                    Transaction
                  </th>

                  <th className="px-6 py-4 font-medium">
                    Amount
                  </th>

                  <th className="px-6 py-4 font-medium">
                    Risk
                  </th>

                  <th className="px-6 py-4 font-medium">
                    Time
                  </th>

                  <th className="px-6 py-4 font-medium">
                    AI Explanation
                  </th>

                </tr>

              </thead>

              <tbody>

                {alerts.map((alert) => (

                  <AlertRow
                    key={alert.id}
                    alert={alert}
                  />

                ))}

              </tbody>

            </table>

          </div>

        </div>

        {/* SHAP CHART */}

        <div className="mt-12">

          <ShapChart
            data={alerts[0]?.shap_explanation || []}
          />

        </div>

      </div>

    </Layout>
  );
}