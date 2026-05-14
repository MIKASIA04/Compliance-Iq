import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { day: "Mon", alerts: 4 },
  { day: "Tue", alerts: 7 },
  { day: "Wed", alerts: 5 },
  { day: "Thu", alerts: 9 },
  { day: "Fri", alerts: 6 },
  { day: "Sat", alerts: 3 },
  { day: "Sun", alerts: 8 },
];

export default function AlertsTrendChart() {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">

      <div className="mb-5">

        <h2 className="text-xl font-semibold text-slate-900">
          Alerts Trend
        </h2>

        <p className="text-sm text-slate-500 mt-1">
          Weekly suspicious activity monitoring
        </p>

      </div>

      <div className="h-[280px] pr-4">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <LineChart
            data={data}
            margin={{
              top: 10,
              right: 30,
              left: 0,
              bottom: 10,
            }}
          >

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e2e8f0"
              vertical={false}
            />

            <XAxis
              dataKey="day"
              tickLine={false}
              axisLine={false}
              padding={{
                left: 20,
                right: 20,
              }}
              tick={{
                fontSize: 13,
                fill: "#64748b",
              }}
            />

            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{
                fontSize: 13,
                fill: "#64748b",
              }}
            />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="alerts"
              stroke="#2563eb"
              strokeWidth={3}
              dot={{
                r: 5,
                strokeWidth: 3,
                fill: "#ffffff",
              }}
              activeDot={{
                r: 7,
              }}
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}