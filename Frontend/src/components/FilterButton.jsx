export default function FilterButton({
  label,
  active,
  onClick,
}) {
  return (
    <button
      onClick={onClick}
      className={`
        px-4 py-2 rounded-xl text-sm font-medium transition-all
        ${
          active
            ? "bg-slate-900 text-white"
            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
        }
      `}
    >
      {label}
    </button>
  );
}