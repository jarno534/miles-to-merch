<template>
  <div class="profile-page">
    <h1>My Profile</h1>
    <div v-if="loading" class="loading">Loading profile...</div>
    <form v-else @submit.prevent="updateProfile" class="profile-form">
      <h2>Account Information</h2>
      <div class="form-group">
        <label for="name">Full Name</label>
        <input
          type="text"
          id="name"
          v-model="user.name"
          placeholder="Enter your full name"
        />
      </div>
      <div class="form-group">
        <label for="email">Email Address</label>
        <input
          type="email"
          id="email"
          v-model="user.email"
          placeholder="Enter your email"
        />
      </div>

      <h2>Shipping Address</h2>
      <div class="form-group">
        <label for="address">Address</label>
        <input
          type="text"
          id="address"
          v-model="user.shipping_address"
          placeholder="Street and number"
        />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="city">City</label>
          <input
            type="text"
            id="city"
            v-model="user.shipping_city"
            placeholder="City"
          />
        </div>
        <div class="form-group">
          <label for="zip">ZIP / Postal Code</label>
          <input
            type="text"
            id="zip"
            v-model="user.shipping_zip"
            placeholder="Postal Code"
          />
        </div>
      </div>
      <div class="form-group">
        <label for="country">Country</label>
        <input
          type="text"
          id="country"
          v-model="user.shipping_country"
          placeholder="Country"
        />
      </div>

      <button type="submit" class="submit-button" :disabled="isSaving">
        {{ isSaving ? "Saving..." : "Save Profile" }}
      </button>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
    </form>
  </div>
</template>

<script>
import axios from "axios";
import { auth } from "../auth";

export default {
  name: "ProfileView",
  data() {
    return {
      user: {},
      loading: true,
      isSaving: false,
      successMessage: "",
    };
  },
  async created() {
    if (!auth.isLoggedIn) {
      this.$router.push("/login");
      return;
    }
    await this.fetchProfile();
  },
  methods: {
    async fetchProfile() {
      try {
        const response = await axios.get("http://localhost:5000/api/profile", {
          withCredentials: true,
        });
        this.user = response.data;
      } catch (error) {
        console.error("Failed to fetch profile:", error);
      } finally {
        this.loading = false;
      }
    },
    async updateProfile() {
      this.isSaving = true;
      this.successMessage = "";
      try {
        await axios.put("http://localhost:5000/api/profile", this.user, {
          withCredentials: true,
        });
        this.successMessage = "Profile updated successfully!";
        setTimeout(() => (this.successMessage = ""), 3000); // Hide message after 3 seconds
      } catch (error) {
        console.error("Failed to update profile:", error);
        alert("Could not update profile. Please try again.");
      } finally {
        this.isSaving = false;
      }
    },
  },
};
</script>

<style scoped>
.profile-page {
  max-width: 700px;
  margin: 40px auto;
  padding: 20px;
}
.profile-form {
  background: #fff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}
h1,
h2 {
  text-align: left;
}
h2 {
  margin-top: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
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
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
}
.form-row {
  display: flex;
  gap: 20px;
}
.form-row .form-group {
  flex: 1;
}
.submit-button {
  width: 100%;
  padding: 15px;
  background-color: #fc4c02;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  margin-top: 20px;
}
.submit-button:disabled {
  background-color: #ccc;
}
.success-message {
  color: #28a745;
  margin-top: 15px;
  text-align: center;
  font-weight: bold;
}
</style>
