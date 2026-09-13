export default function AlertInvestigation({
  alert,
}) {

  if (!alert) return null;

  return (
    <div
      className="
        bg-white
        dark:bg-slate-900

        border
        border-slate-200
        dark:border-slate-800

        rounded-3xl

        shadow-sm

        p-6

        transition-all
      "
    >

      <div className="mb-6">

        <h2
          className="
            text-xl
            font-semibold

            text-slate-900
            dark:text-white
          "
        >
          Alert Investigation
        </h2>

        <p
          className="
            mt-2

            text-slate-500
            dark:text-slate-400
          "
        >
          AI-generated transaction analysis
        </p>

      </div>

      <div
        className="
          grid
          grid-cols-1
          lg:grid-cols-2
          gap-6
        "
      >

        {/* LEFT */}

        <div
          className="
            space-y-4
          "
        >

          <div>

            <p
              className="
                text-sm

                text-slate-500
                dark:text-slate-400
              "
            >
              Transaction ID
            </p>

            <h3
              className="
                mt-1

                text-lg
                font-semibold

                text-slate-900
                dark:text-white
              "
            >
              {alert.transaction_id}
            </h3>

          </div>

          <div>

            <p
              className="
                text-sm

                text-slate-500
                dark:text-slate-400
              "
            >
              Amount
            </p>

            <h3
              className="
                mt-1

                text-lg
                font-semibold

                text-slate-900
                dark:text-white
              "
            >
              ₹{alert.amount.toLocaleString()}
            </h3>

          </div>

          <div>

            <p
              className="
                text-sm

                text-slate-500
                dark:text-slate-400
              "
            >
              Risk Level
            </p>

            <h3
              className="
                mt-1

                text-lg
                font-semibold

                text-red-500
              "
            >
              {alert.risk_level}
            </h3>

          </div>

        </div>

        {/* RIGHT */}

        <div>

          <p
            className="
              text-sm

              text-slate-500
              dark:text-slate-400
            "
          >
            AI Explanation
          </p>

          <div
            className="
              mt-3

              bg-slate-50
              dark:bg-slate-800

              rounded-2xl

              p-5
            "
          >

            <p
              className="
                leading-7

                text-slate-700
                dark:text-slate-300

                whitespace-normal
                break-words
              "
            >
              {alert.ai_explanation}
            </p>

          </div>

        </div>

      </div>

    </div>
  );
}