<template>
  <div class="auth-page">
    <div class="auth-form">
      <h1>Create an Account</h1>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="email">Email Address</label>
          <input type="email" id="email" v-model="email" required />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" class="submit-button">Register</button>
      </form>
      <p class="switch-link">
        Already have an account? <router-link to="/login">Log in</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from '@/apiConfig.js';
import { auth } from "../auth";

export default {
  name: "RegisterView",
  data() {
    return {
      email: "",
      password: "",
      error: null,
    };
  },
  methods: {
    async handleRegister() {
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/auth/register`,
          {
            email: this.email,
            password: this.password,
          },
          { withCredentials: true }
        );

        auth.isLoggedIn = true;
        auth.user = response.data;

        const redirectPath = this.$route.query.redirect;
        if (redirectPath) {
          this.$router.push(redirectPath);
        } else {
          this.$router.push("/");
        }
      } catch (err) {
        this.error =
          err.response?.data?.error || "An unexpected error occurred.";
      }
    },
  },
};
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 50px;
}
.auth-form {
  width: 100%;
  max-width: 400px;
  padding: 30px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}
h1 {
  margin-bottom: 20px;
}
.form-group {
  margin-bottom: 15px;
  text-align: left;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
}
.submit-button {
  width: 100%;
  padding: 12px;
  background-color: #fc4c02;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
}
.error-message {
  color: #dc3545;
  margin-bottom: 15px;
}
.switch-link {
  margin-top: 20px;
}
</style>
