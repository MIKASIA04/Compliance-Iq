import RiskBadge from "./RiskBadge";
import { formatRupees } from "../utils/formatters";

export default function AlertDetails({
  alert,
  onResolve,
  onEscalate,
}) {

  if (!alert) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">

      {/* HEADER */}

      <div className="flex items-start justify-between mb-5">

        <div>
          <h2 className="text-3xl font-semibold text-slate-900">
            Alert Investigation
          </h2>

          <p className="text-sm text-slate-500 mt-1">
            Transaction: {alert.transaction_id}
          </p>
        </div>

        <RiskBadge level={alert.risk_level} />
      </div>

      {/* AMOUNT + STATUS */}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">

        <div className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3">

          <p className="text-[11px] uppercase tracking-wider text-slate-500 mb-1">
            Amount
          </p>

          <p className="text-2xl font-semibold text-slate-900 leading-none">
            {formatRupees(alert.amount)}
          </p>

        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3">

          <p className="text-[11px] uppercase tracking-wider text-slate-500 mb-1">
            Status
          </p>

          <p className="text-2xl font-semibold text-slate-900 capitalize leading-none">
            {alert.status}
          </p>

        </div>

      </div>

      {/* AI EXPLANATION */}

      <div className="mb-6">

        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
          AI Explanation
        </h3>

        <div className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3">

          <p className="text-sm text-slate-700 leading-relaxed">
            {alert.ai_explanation}
          </p>

        </div>

      </div>

      {/* SHAP */}

      <div>

        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
          SHAP Feature Contributions
        </h3>

        <div className="space-y-3">

          {alert.shap_explanation.map((item, index) => (

            <div
              key={index}
              className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3"
            >

              <div className="flex items-center justify-between">

                <div>

                  <p className="text-sm font-semibold text-slate-800 capitalize">
                    {item.feature_name.replace("_", " ")}
                  </p>

                  <p className="text-sm text-slate-500 mt-1">
                    Value: {item.value}
                  </p>

                </div>

                <div className="bg-red-50 text-red-600 text-xs font-semibold px-3 py-1 rounded-lg">
                  +{item.contribution}
                </div>

              </div>

            </div>

          ))}

        </div>

      </div>

      {/* ACTION BUTTONS */}

      <div className="flex items-center gap-3 mt-6">

        <button
          onClick={onResolve}
          className="
            bg-green-600
            hover:bg-green-700
            text-white
            px-4
            py-2.5
            rounded-xl
            text-sm
            font-medium
            transition-all
          "
        >
          Resolve Alert
        </button>

        <button
          onClick={onEscalate}
          className="
            bg-red-600
            hover:bg-red-700
            text-white
            px-4
            py-2.5
            rounded-xl
            text-sm
            font-medium
            transition-all
          "
        >
          Escalate Alert
        </button>

      </div>

    </div>
  );
}