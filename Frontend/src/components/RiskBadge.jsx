import { getRiskColor } from "../utils/formatters";

export default function RiskBadge({ level }) {
  return (
    <span
      className={`
        inline-flex items-center
        px-3 py-1
        rounded-full
        text-xs
        font-semibold
        tracking-wide
        ${getRiskColor(level)}
      `}
    >
      {level?.toUpperCase()}
    </span>
  );
}