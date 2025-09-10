import axios from "axios";

// Je bestaande logica om de juiste URL te bepalen blijft behouden
const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "https://miles-to-merch-backend.onrender.com"
    : "http://localhost:5000";

// --- NIEUWE REGELS ---
// Stel de basis-URL in voor alle toekomstige axios-verzoeken
axios.defaults.baseURL = API_BASE_URL;

// De belangrijkste regel: zorg dat cookies altijd worden meegestuurd
axios.defaults.withCredentials = true;

// Exporteer de volledig geconfigureerde axios-instance
export default axios;