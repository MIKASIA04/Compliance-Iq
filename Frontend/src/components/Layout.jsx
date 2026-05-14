import { useState } from "react";

import { NavLink } from "react-router-dom";

import {
  LayoutDashboard,
  ShieldAlert,
  FileCheck,
  Bell,
  LogOut,
  CheckCheck,
} from "lucide-react";

import toast from "react-hot-toast";

import useAuth from "../hooks/useAuth";

export default function Layout({ children }) {

  const { logout } = useAuth();

  const role =
    sessionStorage.getItem("role");

  const [showNotifications, setShowNotifications] =
    useState(false);

  const [notifications, setNotifications] =
    useState([
      {
        id: 1,
        message:
          "High-risk transaction flagged for AML review.",
        time: "2 mins ago",
        read: false,
      },

      {
        id: 2,
        message:
          "Compliance report updated successfully.",
        time: "15 mins ago",
        read: false,
      },

      {
        id: 3,
        message:
          "KYC verification pending analyst approval.",
        time: "1 hour ago",
        read: true,
      },
    ]);

  const unreadCount =
    notifications.filter(
      (n) => !n.read
    ).length;

  function markAllAsRead() {

    setNotifications((prev) =>
      prev.map((notification) => ({
        ...notification,
        read: true,
      }))
    );

    toast.success(
      "Notifications marked as read"
    );
  }

  const navItems = [
    {
      name: "Dashboard",
      path: "/dashboard",
      icon: LayoutDashboard,
    },

    {
      name: "Alerts",
      path: "/alerts",
      icon: ShieldAlert,
    },

    {
      name: "Compliance",
      path: "/compliance",
      icon: FileCheck,
    },
  ];

  return (
    <div
      className="
        min-h-screen
        flex

        bg-slate-100
        dark:bg-slate-950

        transition-all
      "
    >

      {/* SIDEBAR */}

      <aside
        className="
          hidden
          md:flex
          md:w-64

          bg-slate-900

          text-white

          flex-col

          px-5
          py-6
        "
      >

        {/* LOGO */}

        <div className="mb-10">

          <h1 className="text-3xl font-bold tracking-tight">
            ComplianceIQ
          </h1>

          <p
            className="
              text-slate-400
              text-sm
              mt-2
            "
          >
            AI Compliance Platform
          </p>

        </div>

        {/* NAVIGATION */}

        <nav className="flex flex-col gap-2">

          {navItems.map((item) => {

            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `
                    flex
                    items-center
                    gap-3

                    px-4
                    py-3

                    rounded-xl

                    transition-all

                    ${
                      isActive
                        ? "bg-blue-600 text-white"
                        : "text-slate-300 hover:bg-slate-800"
                    }
                  `
                }
              >

                <Icon size={18} />

                <span
                  className="
                    text-sm
                    font-medium
                  "
                >
                  {item.name}
                </span>

              </NavLink>
            );
          })}

        </nav>

      </aside>

      {/* MAIN */}

      <div className="flex-1 flex flex-col">

        {/* TOPBAR */}

        <header
          className="
            h-16

            bg-white
            dark:bg-slate-900

            border-b
            border-slate-200
            dark:border-slate-800

            flex
            items-center
            justify-between

            px-4
            md:px-8

            transition-all
          "
        >

          {/* LEFT */}

          <div>

            <h2
              className="
                text-sm
                md:text-lg

                font-semibold

                text-slate-900
                dark:text-white
              "
            >
              Compliance Monitoring Dashboard
            </h2>

          </div>

          {/* RIGHT */}

          <div className="flex items-center gap-3">

            {/* NOTIFICATIONS */}

            <div className="relative">

              <button
                onClick={() =>
                  setShowNotifications(
                    !showNotifications
                  )
                }
                className="
                  relative

                  w-10
                  h-10

                  rounded-xl

                  border
                  border-slate-300
                  dark:border-slate-700

                  bg-white
                  dark:bg-slate-800

                  flex
                  items-center
                  justify-center

                  hover:bg-slate-100
                  dark:hover:bg-slate-700

                  transition-all
                "
              >

                <Bell
                  size={18}
                  className="
                    text-slate-700
                    dark:text-slate-200
                  "
                />

                {/* BADGE */}

                {unreadCount > 0 && (

                  <div
                    className="
                      absolute
                      -top-1
                      -right-1

                      w-5
                      h-5

                      rounded-full

                      bg-red-500

                      text-white
                      text-[10px]
                      font-bold

                      flex
                      items-center
                      justify-center
                    "
                  >
                    {unreadCount}
                  </div>

                )}

              </button>

              {/* DROPDOWN */}

              {showNotifications && (

                <div
                  className="
                    absolute
                    right-0
                    top-14

                    w-[360px]

                    bg-white
                    dark:bg-slate-900

                    border
                    border-slate-200
                    dark:border-slate-800

                    rounded-2xl

                    shadow-xl

                    overflow-hidden

                    z-50
                  "
                >

                  {/* HEADER */}

                  <div
                    className="
                      flex
                      items-center
                      justify-between

                      px-5
                      py-4

                      border-b
                      border-slate-200
                      dark:border-slate-800
                    "
                  >

                    <div>

                      <h3
                        className="
                          font-semibold

                          text-slate-900
                          dark:text-white
                        "
                      >
                        Notifications
                      </h3>

                      <p
                        className="
                          text-xs

                          text-slate-500
                          dark:text-slate-400

                          mt-1
                        "
                      >
                        Recent compliance activity
                      </p>

                    </div>

                    <button
                      onClick={markAllAsRead}
                      className="
                        flex
                        items-center
                        gap-1

                        text-xs
                        font-medium

                        text-blue-600

                        hover:underline
                      "
                    >

                      <CheckCheck size={14} />

                      Mark all read

                    </button>

                  </div>

                  {/* ITEMS */}

                  <div className="max-h-[320px] overflow-y-auto">

                    {notifications.map(
                      (notification) => (

                        <div
                          key={notification.id}

                          className={`
                            px-5
                            py-4

                            border-b
                            border-slate-100
                            dark:border-slate-800

                            transition-all

                            ${
                              !notification.read
                                ? `
                                  bg-blue-50
                                  dark:bg-blue-950/20
                                `
                                : ""
                            }
                          `}
                        >

                          <p
                            className="
                              text-sm

                              leading-6

                              text-slate-700
                              dark:text-slate-300
                            "
                          >
                            {notification.message}
                          </p>

                          <p
                            className="
                              text-xs

                              mt-2

                              text-slate-400
                            "
                          >
                            {notification.time}
                          </p>

                        </div>

                      )
                    )}

                  </div>

                </div>

              )}

            </div>

            {/* PROFILE */}

            <div
              className="
                hidden
                sm:flex

                items-center
                gap-4

                bg-white
                dark:bg-slate-800

                border
                border-slate-200
                dark:border-slate-700

                rounded-2xl

                px-4
                py-2

                shadow-sm
              "
            >

              {/* AVATAR */}

              <div
                className="
                  w-11
                  h-11

                  rounded-full

                  bg-blue-600

                  flex
                  items-center
                  justify-center

                  text-white
                  font-semibold
                  text-lg
                "
              >
                {role?.charAt(0).toUpperCase()}
              </div>

              {/* USER */}

              <div>

                <p
                  className="
                    text-sm
                    font-semibold

                    text-slate-900
                    dark:text-white
                  "
                >

                  {
                    role === "admin"
                      ? "Admin User"
                      : role === "analyst"
                      ? "Risk Analyst"
                      : "Compliance Officer"
                  }

                </p>

                <p
                  className="
                    text-xs

                    text-slate-500
                    dark:text-slate-400
                  "
                >

                  {
                    role === "admin"
                      ? "System Administrator"
                      : role === "analyst"
                      ? "Fraud Investigation Team"
                      : "Regulatory Oversight"
                  }

                </p>

              </div>

              {/* LOGOUT */}

              <button
                onClick={() => {

                  toast.success(
                    "Logged out successfully"
                  );

                  logout();
                }}
                className="
                  flex
                  items-center
                  gap-2

                  px-3
                  py-2

                  rounded-xl

                  bg-slate-100
                  dark:bg-slate-700

                  hover:bg-slate-200
                  dark:hover:bg-slate-600

                  text-slate-700
                  dark:text-slate-200

                  text-sm
                  font-medium

                  transition-all
                "
              >

                <LogOut size={16} />

                Sign Out

              </button>

            </div>

          </div>

        </header>

        {/* CONTENT */}

        <main
          className="
            flex-1

            p-4
            md:p-8

            text-slate-900
            dark:text-white

            transition-all
          "
        >

          {children}

        </main>

      </div>

    </div>
  );
}