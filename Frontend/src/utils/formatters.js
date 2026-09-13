import { formatDistanceToNow } from "date-fns";

export function formatRupees(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatRelativeTime(date) {
  return formatDistanceToNow(new Date(date), {
    addSuffix: true,
  });
}

export function getRiskColor(level) {
  switch (level?.toLowerCase()) {
    case "high":
      return "text-red-700 bg-red-100";

    case "medium":
      return "text-amber-700 bg-amber-100";

    case "low":
      return "text-green-700 bg-green-100";

    default:
      return "text-slate-700 bg-slate-100";
  }
}