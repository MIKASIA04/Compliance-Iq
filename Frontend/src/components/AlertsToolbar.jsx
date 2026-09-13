import FilterButton from "./FilterButton";

export default function AlertsToolbar({
  search,
  setSearch,
  riskFilter,
  setRiskFilter,
  statusFilter,
  setStatusFilter,
  sortBy,
  setSortBy,
}) {
  return (
    <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-4 mb-6">

      {/* SEARCH */}

      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search transaction ID..."
        className="w-full xl:w-80 px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <div className="flex flex-wrap items-center gap-3">

        {/* RISK FILTER */}

        <div className="flex items-center gap-2">

          <FilterButton
            label="All"
            active={riskFilter === "all"}
            onClick={() => setRiskFilter("all")}
          />

          <FilterButton
            label="High"
            active={riskFilter === "high"}
            onClick={() => setRiskFilter("high")}
          />

          <FilterButton
            label="Medium"
            active={riskFilter === "medium"}
            onClick={() => setRiskFilter("medium")}
          />

          <FilterButton
            label="Low"
            active={riskFilter === "low"}
            onClick={() => setRiskFilter("low")}
          />

        </div>

        {/* STATUS FILTER */}

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-3 rounded-xl border border-slate-300 bg-white focus:outline-none"
        >
          <option value="all">All Status</option>
          <option value="open">Open</option>
          <option value="resolved">Resolved</option>
        </select>

        {/* SORT */}

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-3 rounded-xl border border-slate-300 bg-white focus:outline-none"
        >
          <option value="latest">Latest</option>
          <option value="highest">Highest Amount</option>
          <option value="lowest">Lowest Amount</option>
        </select>

      </div>

    </div>
  );
}