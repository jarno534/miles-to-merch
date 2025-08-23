<template>
  <div class="profile-page">
    <div v-if="!auth.isAuthCheckComplete" class="loading">
      Authenticating...
    </div>
    <template v-else>
      <h1>My Profile</h1>
      <SpinnerComponent v-if="loading" text="Loading profile..." />
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

        <h2>Integrations</h2>
        <div class="form-group">
          <div v-if="user.has_strava_linked" class="strava-linked">
            <p>✓ Strava Account Linked</p>
          </div>
          <div v-else>
            <p>Connect your Strava account to easily use your activities.</p>
            <a
              href="http://localhost:5000/auth/login/strava?next=profile"
              class="strava-button"
              >Link Strava Account</a
            >
          </div>
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
        <p v-if="successMessage" class="success-message">
          {{ successMessage }}
        </p>

        <div class="delete-section">
          <button @click.prevent="showDeleteModal" class="delete-button">
            Delete My Account
          </button>
        </div>
      </form>
    </template>
    <transition name="modal-fade">
      <div
        v-if="isDeleteModalVisible"
        class="modal-backdrop"
        @click.self="cancelDelete"
      >
        <div class="modal-content">
          <h3 class="modal-title">Confirm Account Deletion</h3>
          <p class="modal-message">
            Please enter your password to confirm. This action cannot be undone.
          </p>
          <div class="form-group">
            <label for="password-confirm">Password</label>
            <input
              type="password"
              id="password-confirm"
              v-model="passwordForDelete"
              @keyup.enter="confirmDelete"
            />
          </div>
          <div v-if="deleteError" class="error-message">{{ deleteError }}</div>
          <div class="modal-actions">
            <button @click="cancelDelete" class="button-secondary">
              Cancel
            </button>
            <button @click="confirmDelete" class="button-danger">
              Confirm & Delete
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from "axios";
import { auth } from "../auth";
import { notifySuccess, notifyError } from "../notifications";
import SpinnerComponent from "@/components/SpinnerComponent.vue";

export default {
  name: "ProfileView",
  components: { SpinnerComponent },
  data() {
    return {
      user: {},
      loading: true,
      isSaving: false,
      successMessage: "",
      isDeleteModalVisible: false,
      passwordForDelete: "",
      deleteError: null,
      auth: auth,
    };
  },
  watch: {
    "auth.isAuthCheckComplete"(isComplete) {
      if (isComplete) {
        this.handleAuthCheck();
      }
    },
  },
  created() {
    if (auth.isAuthCheckComplete) {
      this.handleAuthCheck();
    }
  },
  methods: {
    handleAuthCheck() {
      if (!auth.isLoggedIn) {
        this.$router.push("/login");
      } else {
        this.fetchProfile();
      }
    },
    async fetchProfile() {
      this.loading = true;
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
      try {
        await axios.put("http://localhost:5000/api/profile", this.user, {
          withCredentials: true,
        });
        notifySuccess("Profile updated successfully!");
        setTimeout(() => (this.successMessage = ""), 3000);
      } catch (error) {
        console.error("Failed to update profile:", error);
        notifyError("Could not update profile. Please try again.");
      } finally {
        this.isSaving = false;
      }
    },
    showDeleteModal() {
      this.isDeleteModalVisible = true;
      this.deleteError = null;
      this.passwordForDelete = "";
    },
    cancelDelete() {
      this.isDeleteModalVisible = false;
    },
    async confirmDelete() {
      this.deleteError = null;
      if (!this.passwordForDelete) {
        this.deleteError = "Password is required.";
        return;
      }
      try {
        await axios.post(
          "http://localhost:5000/api/profile/delete",
          { password: this.passwordForDelete },
          { withCredentials: true }
        );

        auth.isLoggedIn = false;
        auth.user = null;

        this.$router.push("/");
        notifySuccess("Your account has been successfully deleted.");
      } catch (error) {
        this.deleteError = error.response?.data?.error || "An error occurred.";
        console.error("Failed to delete account:", error);
      }
    },
  },
};
</script>

<style scoped>
/* Je bestaande stijlen blijven ongewijzigd */
.profile-page {
  max-width: 700px;
  margin: 40px auto;
  padding: 20px;
}
.loading {
  text-align: center;
  margin-top: 50px;
  color: #666;
  font-size: 1.2rem;
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
.strava-linked p {
  color: #28a745;
  font-weight: bold;
  margin: 0;
  padding: 10px;
  background-color: #e9f7ef;
  border-radius: 5px;
}
.strava-button {
  display: inline-block;
  background-color: #fc4c02;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
}
.delete-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: right;
}
.delete-button {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  text-decoration: underline;
  font-size: 0.9em;
}
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
}
.modal-title {
  margin-top: 0;
  font-size: 1.5rem;
}
.modal-message {
  margin-bottom: 25px;
  line-height: 1.6;
  color: #555;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 20px;
}
.modal-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
.button-secondary {
  background-color: #f0f2f5;
}
.button-danger {
  background-color: #dc3545;
  color: white;
}
.error-message {
  color: #dc3545;
  margin-top: 10px;
}
</style>
