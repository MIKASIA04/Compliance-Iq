import { useNavigate } from "react-router-dom";

export default function useAuth() {

  const navigate = useNavigate();

  function login(token, role) {

    sessionStorage.setItem(
      "token",
      token
    );

    sessionStorage.setItem(
      "role",
      role
    );

    navigate("/dashboard");
  }

  function logout() {

    sessionStorage.removeItem(
      "token"
    );

    sessionStorage.removeItem(
      "role"
    );

    navigate("/");
  }

  function isAuthenticated() {

    return !!sessionStorage.getItem(
      "token"
    );
  }

  function getRole() {

    return sessionStorage.getItem(
      "role"
    );
  }

  return {
    login,
    logout,
    isAuthenticated,
    getRole,
  };
}