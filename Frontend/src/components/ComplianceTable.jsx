const complianceData = [
  {
    regulation: "AML Monitoring",
    status: "Compliant",
    updated: "2 hours ago",
  },

  {
    regulation: "KYC Verification",
    status: "Pending Review",
    updated: "5 hours ago",
  },

  {
    regulation: "Transaction Screening",
    status: "Compliant",
    updated: "1 day ago",
  },

  {
    regulation: "Fraud Detection",
    status: "Active Monitoring",
    updated: "30 mins ago",
  },
];

export default function ComplianceTable() {

  return (
    <div
      className="
        bg-white
        dark:bg-slate-900

        border
        border-slate-200
        dark:border-slate-800

        rounded-2xl

        shadow-sm

        p-6

        transition-all
      "
    >

      {/* HEADER */}

      <div className="mb-5">

        <h2
          className="
            text-xl
            font-semibold

            text-slate-900
            dark:text-white
          "
        >
          Compliance Summary
        </h2>

        <p
          className="
            text-sm

            text-slate-500
            dark:text-slate-400

            mt-1
          "
        >
          Regulatory monitoring overview
        </p>

      </div>

      {/* TABLE */}

      <div className="overflow-x-auto">

        <table className="w-full">

          <thead>

            <tr
              className="
                border-b
                border-slate-200
                dark:border-slate-800
              "
            >

              <th
                className="
                  text-left

                  py-3

                  text-sm
                  font-semibold

                  text-slate-600
                  dark:text-slate-300
                "
              >
                Regulation
              </th>

              <th
                className="
                  text-left

                  py-3

                  text-sm
                  font-semibold

                  text-slate-600
                  dark:text-slate-300
                "
              >
                Status
              </th>

              <th
                className="
                  text-left

                  py-3

                  text-sm
                  font-semibold

                  text-slate-600
                  dark:text-slate-300
                "
              >
                Last Updated
              </th>

            </tr>

          </thead>

          <tbody>

            {complianceData.map(
              (item, index) => (

                <tr
                  key={index}

                  className="
                    border-b
                    border-slate-100
                    dark:border-slate-800

                    hover:bg-slate-50
                    dark:hover:bg-slate-800/40

                    transition-all
                  "
                >

                  {/* REGULATION */}

                  <td
                    className="
                      py-4

                      text-sm

                      text-slate-800
                      dark:text-slate-200
                    "
                  >
                    {item.regulation}
                  </td>

                  {/* STATUS */}

                  <td className="py-4">

                    <span
                      className={`
                        px-3
                        py-1

                        rounded-full

                        text-xs
                        font-medium

                        ${
                          item.status ===
                          "Compliant"
                            ? `
                              bg-green-100
                              text-green-700
                            `
                            : item.status ===
                              "Pending Review"
                            ? `
                              bg-amber-100
                              text-amber-700
                            `
                            : `
                              bg-blue-100
                              text-blue-700
                            `
                        }
                      `}
                    >

                      {item.status}

                    </span>

                  </td>

                  {/* UPDATED */}

                  <td
                    className="
                      py-4

                      text-sm

                      text-slate-500
                      dark:text-slate-400
                    "
                  >
                    {item.updated}
                  </td>

                </tr>

              )
            )}

          </tbody>

        </table>

      </div>

    </div>
  );
}