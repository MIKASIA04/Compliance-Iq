import {
  Moon,
  Sun,
} from "lucide-react";

import useTheme
from "../hooks/useTheme";

export default function ThemeToggle() {

  const {
    darkMode,
    toggleTheme,
  } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="
        w-10
        h-10

        rounded-xl

        border
        border-slate-300

        bg-white

        flex
        items-center
        justify-center

        transition-all

        hover:bg-slate-100
      "
    >

      {darkMode ? (

        <Sun
          size={18}
          className="text-yellow-500"
        />

      ) : (

        <Moon
          size={18}
          className="text-slate-700"
        />

      )}

    </button>
  );
}