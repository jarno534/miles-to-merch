<template>
  <nav class="main-nav">
    <div class="nav-links">
      <router-link to="/">Home</router-link>
      <router-link v-if="auth.isLoggedIn" to="/my-designs"
        >My Designs</router-link
      >
      |
      <router-link v-if="auth.isLoggedIn" to="/profile">Profile</router-link>
    </div>
    <div class="nav-auth">
      <template v-if="auth.isLoggedIn">
        <button @click="logout" class="nav-button">Logout</button>
      </template>
      <template v-else>
        <router-link to="/login" class="nav-button">Login</router-link>
        <router-link to="/register" class="nav-button register"
          >Register</router-link
        >
      </template>
    </div>
  </nav>
  <router-view />
</template>

<script>
import { auth } from "./auth";
import axios from "axios";
import { useRouter } from "vue-router";

export default {
  setup() {
    const router = useRouter();

    const logout = async () => {
      try {
        await axios.post(
          "http://localhost:5000/auth/logout",
          {},
          { withCredentials: true }
        );
        auth.isLoggedIn = false;
        auth.user = null;
        // Redirect to homepage after logout
        router.push("/");
      } catch (error) {
        console.error("Logout failed:", error);
      }
    };

    return {
      auth,
      logout,
    };
  },
  async created() {
    // Check login status every time the app is loaded
    await auth.checkAuthStatus();
  },
};
</script>

<style>
/* You can keep your existing #app styles */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

/* New styles for the navigation bar */
.main-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-links a,
.nav-auth a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 15px;
  transition: color 0.2s;
}

.nav-links a:hover {
  color: #fc4c02;
}

.nav-links a.router-link-exact-active {
  color: #fc4c02;
  border-bottom: 2px solid #fc4c02;
  padding-bottom: 5px;
}

.nav-auth {
  display: flex;
  align-items: center;
}

.nav-button {
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  font-size: 1em;
  margin-left: 10px;
  transition: background-color 0.2s, color 0.2s;
}

.nav-button.register {
  background-color: #fc4c02;
  color: white;
}
.nav-button.register:hover {
  background-color: #e24300;
}

.nav-button:not(.register) {
  background-color: #f0f2f5;
  color: #333;
}
.nav-button:not(.register):hover {
  background-color: #e2e6ea;
}
</style>
