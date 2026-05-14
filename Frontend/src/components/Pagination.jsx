export default function Pagination({
  currentPage,
  totalPages,
  setCurrentPage,
}) {
  return (
    <div className="flex items-center justify-between mt-6">

      <button
        disabled={currentPage === 1}
        onClick={() =>
          setCurrentPage(currentPage - 1)
        }
        className="
          px-4 py-2 rounded-xl border border-slate-300
          disabled:opacity-50
          hover:bg-slate-100
          transition-all
        "
      >
        Previous
      </button>

      <div className="flex items-center gap-2">

        {Array.from(
          { length: totalPages },
          (_, index) => (

            <button
              key={index}
              onClick={() =>
                setCurrentPage(index + 1)
              }
              className={`
                w-8 h-8 rounded-lg text-xs font-medium transition-all
                ${
                  currentPage === index + 1
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }
              `}
            >
              {index + 1}
            </button>

          )
        )}

      </div>

      <button
        disabled={currentPage === totalPages}
        onClick={() =>
          setCurrentPage(currentPage + 1)
        }
        className="
          px-4 py-2 rounded-xl border border-slate-300
          disabled:opacity-50
          hover:bg-slate-100
          transition-all
        "
      >
        Next
      </button>

    </div>
  );
}