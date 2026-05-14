const stats = [
  {
    title: "Active Policies",
    value: "128",
  },

  {
    title: "Pending Reviews",
    value: "14",
  },

  {
    title: "Risk Alerts",
    value: "23",
  },

  {
    title: "Compliance Score",
    value: "94%",
  },
];

export default function ComplianceStats() {
  return (
    <div
      className="
        grid
        grid-cols-1
        sm:grid-cols-2
        xl:grid-cols-4
        gap-6
      "
    >

      {stats.map((stat, index) => (

        <div
          key={index}
          className="
            bg-white
            dark:bg-slate-900

            border
            border-slate-200
            dark:border-slate-800

            rounded-2xl

            p-5

            shadow-sm

            transition-all
          "
        >

          <p
            className="
              text-sm
              text-slate-500
              dark:text-slate-400
            "
          >
            {stat.title}
          </p>

          <h2
            className="
              mt-3

              text-3xl
              font-bold

              text-slate-900
              dark:text-white
            "
          >
            {stat.value}
          </h2>

        </div>

      ))}

    </div>
  );
}