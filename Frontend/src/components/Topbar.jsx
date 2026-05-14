export default function TopBar() {
  return (
    <header className="h-12 bg-white border-b border-slate-200 flex items-center justify-end px-6">

      <div className="flex items-center gap-3">

        <div className="text-right leading-tight">
          <p className="text-sm font-medium text-slate-800">
            Admin User
          </p>

          <p className="text-[11px] text-slate-500">
            admin@complianceiq.com
          </p>
        </div>

        <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-semibold">
          A
        </div>

      </div>

    </header>
  );
}