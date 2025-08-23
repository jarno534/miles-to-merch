// src/auth.js
import { reactive } from "vue";
import axios from "axios";

// A reactive object to hold our user's state
export const auth = reactive({
  isLoggedIn: false,
  user: null,

  // A function to check the backend for the current auth status
  async checkAuthStatus() {
    try {
      const response = await axios.get("http://localhost:5000/auth/status", {
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
      console.error("Not authenticated:", error);
      this.isLoggedIn = false;
      this.user = null;
    }
  },
});
