import Layout from "../components/Layout";

import ComplianceStats from "../components/ComplianceStats";
import RiskPieChart from "../components/RiskPieChart";
import AlertsTrendChart from "../components/AlertsTrendChart";
import ComplianceTable from "../components/ComplianceTable";

export default function Compliance() {
  return (
    <Layout>

      <div className="space-y-8">

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
            Compliance Center
          </h1>

          <p
            className="
              text-slate-500
              dark:text-slate-400

              mt-2
            "
          >
            Regulatory monitoring and compliance analytics
          </p>

        </div>

        {/* STATS */}

        <ComplianceStats />

        {/* CHARTS */}

        <div
          className="
            grid
            grid-cols-1
            xl:grid-cols-2
            gap-6
          "
        >

          <RiskPieChart />

          <AlertsTrendChart />

        </div>

        {/* TABLE */}

        <ComplianceTable />

      </div>

    </Layout>
  );
}