<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <h2>Complete Your Profile</h2>
      <p>Please provide your shipping details to continue.</p>

      <form @submit.prevent="saveProfile">
        <div class="form-group" v-if="!user.email">
          <label>Email Address</label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="name@example.com"
          />
        </div>

        <div class="form-group">
          <label>Full Name</label>
          <input v-model="form.name" type="text" required />
        </div>

        <div class="form-group">
          <label>Address (Street + Nr)</label>
          <input
            v-model="form.shipping_address"
            type="text"
            required
            placeholder="Main Street 123"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Zip Code</label>
            <input v-model="form.shipping_zip" type="text" required />
          </div>
          <div class="form-group">
            <label>City</label>
            <input v-model="form.shipping_city" type="text" required />
          </div>
        </div>

        <div class="form-group">
          <label>Country</label>
          <input v-model="form.shipping_country" type="text" required />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <div class="actions">
          <button type="button" @click="$emit('close')" class="cancel-btn">
            Cancel
          </button>
          <button type="submit" class="save-btn" :disabled="loading">
            {{ loading ? "Saving..." : "Save & Continue" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "@/apiConfig.js";

export default {
  name: "CompleteProfileModal",
  props: {
    user: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      form: {
        email: this.user.email || "",
        name: this.user.name || "",
        shipping_address: this.user.shipping_address || "",
        shipping_zip: this.user.shipping_zip || "",
        shipping_city: this.user.shipping_city || "",
        shipping_country: this.user.shipping_country || "",
      },
      loading: false,
      error: null,
    };
  },
  methods: {
    async saveProfile() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.put("/api/profile", this.form, {
          withCredentials: true,
        });
        this.$emit("saved", response.data);
      } catch (err) {
        console.error("Profile save failed", err);
        this.error = err.response?.data?.error || "Failed to save profile.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}
h2 {
  margin-top: 0;
  color: #2c3e50;
}
.form-group {
  margin-bottom: 15px;
  text-align: left;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 15px;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}
input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}
.error-msg {
  color: red;
  margin-bottom: 15px;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
.save-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
.cancel-btn {
  background: #eee;
  color: #333;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}
</style>
