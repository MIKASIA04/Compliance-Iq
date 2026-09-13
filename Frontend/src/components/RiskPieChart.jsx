import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { name: "High Risk", value: 12 },
  { name: "Medium Risk", value: 18 },
  { name: "Low Risk", value: 34 },
];

const COLORS = [
  "#ef4444",
  "#f59e0b",
  "#22c55e",
];

export default function RiskPieChart() {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">

      <div className="mb-5">

        <h2 className="text-xl font-semibold text-slate-900">
          Risk Distribution
        </h2>

        <p className="text-sm text-slate-500 mt-1">
          Alert severity overview
        </p>

      </div>

      <div className="h-64">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <PieChart>

            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={85}
              innerRadius={52}
              paddingAngle={3}
            >

              {data.map((entry, index) => (

                <Cell
                  key={index}
                  fill={COLORS[index]}
                />

              ))}

            </Pie>

            <Tooltip />

          </PieChart>

        </ResponsiveContainer>

      </div>

      <div className="flex items-center justify-center gap-6 mt-4">

        {data.map((item, index) => (

          <div
            key={index}
            className="flex items-center gap-2"
          >

            <div
              className="w-3 h-3 rounded-full"
              style={{
                backgroundColor: COLORS[index],
              }}
            />

            <p className="text-sm text-slate-600">
              {item.name}
            </p>

          </div>

        ))}

      </div>

    </div>
  );
}