import axios from "axios";

const API = axios.create({

  baseURL: "http://localhost:5000",

});

export async function getAlerts() {

  const response =
    await API.get("/alerts");

  return response.data;

}

export async function loginUser(data) {

  const response =
    await API.post(
      "/login",
      data
    );

  return response.data;

}
export async function getDashboardStats() {

  const response =
    await API.get(
      "/dashboard-stats"
    );

  return response.data;

}

export async function resolveAlert(id) {

  const response =
    await API.patch(
      `/alerts/${id}/resolve`
    );

  return response.data;

}

export async function escalateAlert(id) {

  const response =
    await API.patch(
      `/alerts/${id}/escalate`
    );

  return response.data;

}