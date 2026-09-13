export default function AlertRow({
  alert,
  onClick,
}) {

  const riskLevel =
    alert.risk_level.toLowerCase();

  return (
    <tr
      onClick={onClick}
      className="
        border-t
        border-slate-100
        dark:border-slate-800

        hover:bg-slate-50
        dark:hover:bg-slate-800/60

        cursor-pointer

        transition-all
      "
    >

      <td
        className="
          px-6
          py-5

          font-medium

          text-slate-900
          dark:text-white
        "
      >
        {alert.transaction_id}
      </td>

      <td
        className="
          px-6
          py-5

          text-slate-700
          dark:text-slate-300
        "
      >
        ₹{alert.amount.toLocaleString()}
      </td>

      <td className="px-6 py-5">

        <span
          className={`
            px-3
            py-1

            rounded-full

            text-xs
            font-semibold

            ${
              riskLevel === "high"
                ? "bg-red-100 text-red-600"

                : riskLevel === "medium"
                ? "bg-amber-100 text-amber-700"

                : "bg-green-100 text-green-700"
            }
          `}
        >

          {alert.risk_level}

        </span>

      </td>

      <td
        className="
          px-6
          py-5

          capitalize

          text-slate-700
          dark:text-slate-300
        "
      >
        {alert.status}
      </td>

      <td
        className="
          px-6
          py-5

          text-slate-500
          dark:text-slate-400
        "
      >
        {alert.created_at}
      </td>

      <td
        className="
          px-6
          py-5

          text-slate-600
          dark:text-slate-300

          max-w-[320px]
          truncate
        "
      >
        {alert.ai_explanation}
      </td>

    </tr>
  );
}