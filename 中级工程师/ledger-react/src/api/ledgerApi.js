import axios from "axios";

const client = axios.create({
  baseURL: "",
  headers: {
    "Content-Type": "application/json"
  }
});

function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`
  };
}

export async function login(username, password) {
  const { data } = await client.post("/login", { username, password });
  return data;
}

export async function register(username, password) {
  const { data } = await client.post("/register", { username, password });
  return data;
}

export async function fetchRecords(token, type) {
  const { data } = await client.get("/records", {
    params: type ? { type } : {},
    headers: authHeaders(token)
  });
  return data;
}

export async function createRecord(token, record) {
  const { data } = await client.post("/records", record, {
    headers: authHeaders(token)
  });
  return data;
}

export async function deleteRecord(token, id) {
  const { data } = await client.delete(`/records/${id}`, {
    headers: authHeaders(token)
  });
  return data;
}

export async function fetchStats(token) {
  const { data } = await client.get("/records/stats", {
    headers: authHeaders(token)
  });
  return data;
}
