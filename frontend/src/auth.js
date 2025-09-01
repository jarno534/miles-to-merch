import { reactive } from "vue";
import axios from "axios";
import API_BASE_URL from "@/apiConfig";

export const auth = reactive({
  isLoggedIn: false,
  user: null,
  isAuthCheckComplete: false,

  async checkAuthStatus() {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/status`, {
        withCredentials: true,
      });
      if (response.data.logged_in) {
        this.isLoggedIn = true;
        this.user = response.data.user;
      } else {
        this.isLoggedIn = false;
        this.user = null;
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      this.isLoggedIn = false;
      this.user = null;
    } finally {
      this.isAuthCheckComplete = true;
    }
  },
});
