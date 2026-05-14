export default function StatCard({
  title,
  value,
  borderColor,
}) {

  return (
    <div
      className={`
        bg-white
        dark:bg-slate-900

        rounded-2xl

        border
        border-slate-200
        dark:border-slate-800

        border-l-4
        ${borderColor}

        shadow-sm

        px-5
        md:px-6

        py-4
        md:py-5

        transition-all
      `}
    >

      <p
        className="
          text-sm

          text-slate-500
          dark:text-slate-400
        "
      >
        {title}
      </p>

      <h2
        className="
          mt-3

          text-2xl
          md:text-3xl

          font-bold

          text-slate-900
          dark:text-white
        "
      >
        {value}
      </h2>

    </div>
  );
}