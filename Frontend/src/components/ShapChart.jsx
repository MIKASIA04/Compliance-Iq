import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

export default function ShapChart({
  data,
}) {

  return (
    <div
      className="
        bg-white
        dark:bg-slate-900

        border
        border-slate-200
        dark:border-slate-800

        rounded-2xl

        p-6

        shadow-sm

        transition-all

        overflow-x-auto
      "
    >

      {/* HEADER */}

      <div className="mb-6">

        <h2
          className="
            text-lg
            font-semibold

            text-slate-900
            dark:text-white
          "
        >
          AI Feature Importance
        </h2>

        <p
          className="
            text-sm

            text-slate-500
            dark:text-slate-400

            mt-1
          "
        >
          SHAP-based transaction explanation
        </p>

      </div>

      {/* CHART */}

      <div className="min-w-[700px]">

        <BarChart
          width={700}
          height={350}
          data={data}
        >

          <XAxis
            dataKey="feature"

            tick={{
              fill: "#64748b",
              fontSize: 12,
            }}
          />

          <YAxis
            tick={{
              fill: "#64748b",
              fontSize: 12,
            }}
          />

          <Tooltip />

          <Bar
            dataKey="impact"
            radius={[8, 8, 0, 0]}
          />

        </BarChart>

      </div>

    </div>
  );
}