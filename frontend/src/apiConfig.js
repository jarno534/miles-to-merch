import axios from "axios";

const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "https://miles-to-merch-backend.onrender.com"
    : "http://localhost:5000";

axios.defaults.baseURL = API_BASE_URL;

axios.defaults.withCredentials = true;

export default axios;
