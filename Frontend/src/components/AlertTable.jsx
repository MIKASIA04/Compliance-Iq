import RiskBadge from "./RiskBadge";

import {
  formatRupees,
  formatRelativeTime,
} from "../utils/formatters";

export default function AlertTable({
  alerts,
  selectedAlert,
  onSelect,
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200">

      <table className="w-full">

        <thead className="bg-slate-50">

          <tr className="text-left text-sm text-slate-500">

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
              AI Explanation
            </th>

          </tr>

        </thead>

        <tbody>

          {alerts.map((alert) => {

            const isSelected =
              selectedAlert?.id === alert.id;

            return (

              <tr
                key={alert.id}
                onClick={() => onSelect(alert)}
                className={`
                  border-t border-slate-100
                  transition-all cursor-pointer
                  hover:bg-slate-50
                  ${
                    isSelected
                      ? "bg-blue-50"
                      : ""
                  }
                `}
              >

                <td className="px-6 py-5 font-medium text-slate-700">
                  {alert.transaction_id}
                </td>

                <td className="px-6 py-5">
                  {formatRupees(alert.amount)}
                </td>

                <td className="px-6 py-5">
                  <RiskBadge level={alert.risk_level} />
                </td>

                <td className="px-6 py-5 capitalize text-slate-600">
                  {alert.status}
                </td>

                <td className="px-6 py-5 text-slate-500">
                  {formatRelativeTime(alert.created_at)}
                </td>

                <td className="px-6 py-5 text-slate-600 max-w-md">
                  <p className="truncate">
                    {alert.ai_explanation}
                  </p>
                </td>

              </tr>

            );
          })}

        </tbody>

      </table>

    </div>
  );
}