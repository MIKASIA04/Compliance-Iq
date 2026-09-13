import {
  createContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const ThemeContext = createContext(null);

export default function ThemeProvider({
  children,
}) {

  const [darkMode, setDarkMode] =
    useState(() => {

      return (
        localStorage.getItem(
          "darkMode"
        ) === "true"
      );

    });

  useEffect(() => {

    if (darkMode) {

      document.documentElement.classList.add(
        "dark"
      );

    } else {

      document.documentElement.classList.remove(
        "dark"
      );

    }

    localStorage.setItem(
      "darkMode",
      darkMode
    );

  }, [darkMode]);

  function toggleTheme() {

    setDarkMode((prev) => !prev);

  }

  const value = useMemo(() => {

    return {
      darkMode,
      toggleTheme,
    };

  }, [darkMode]);

  return (
    <ThemeContext.Provider value={value}>

      {children}

    </ThemeContext.Provider>
  );
}

export { ThemeContext };