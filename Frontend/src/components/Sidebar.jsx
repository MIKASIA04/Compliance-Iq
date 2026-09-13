import {
  LayoutDashboard,
  AlertTriangle,
  ShieldCheck,
  LogOut,
} from "lucide-react";

import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="w-52 min-h-screen bg-slate-900 text-white flex flex-col">

      <div className="px-5 py-7 border-b border-slate-800">
        <h1 className="text-2xl font-bold tracking-tight">
          ComplianceIQ
        </h1>

        <p className="text-slate-400 text-sm mt-2">
          AI Compliance Monitoring
        </p>
      </div>

      <nav className="flex-1 px-3 py-6 space-y-2">

        <NavLink
          to="/"
          className={({ isActive }) =>
            `w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
              isActive
                ? "bg-slate-800 text-white"
                : "hover:bg-slate-800 text-slate-200"
            }`
          }
        >
          <LayoutDashboard size={20} />
          Dashboard
        </NavLink>

        <NavLink
          to="/alerts"
          className={({ isActive }) =>
            `w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
              isActive
                ? "bg-slate-800 text-white"
                : "hover:bg-slate-800 text-slate-200"
            }`
          }
        >
          <AlertTriangle size={20} />
          Alerts
        </NavLink>

        <NavLink
          to="/compliance"
          className={({ isActive }) =>
            `w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
              isActive
                ? "bg-slate-800 text-white"
                : "hover:bg-slate-800 text-slate-200"
            }`
          }
        >
          <ShieldCheck size={20} />
          Compliance
        </NavLink>

      </nav>

      <div className="p-3 border-t border-slate-800">

        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 transition-colors text-red-400">
          <LogOut size={20} />
          Logout
        </button>

      </div>

    </aside>
  );
}