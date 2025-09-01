<template>
  <div class="checkout-page">
    <h1>Review Your Order</h1>
    <div v-if="loading" class="loading">Loading your order details...</div>
    <div v-else class="checkout-container">
      <div class="order-summary">
        <h2>Order Summary</h2>
        <div v-if="product" class="product-item">
          <img
            :src="product.image_url"
            :alt="product.name"
            class="product-thumbnail"
          />
          <div class="product-details">
            <h3>{{ product.name }}</h3>
            <p>Your custom design based on "{{ design.name }}"</p>
            <p class="price">€{{ product.price.toFixed(2) }}</p>
          </div>
        </div>
        <div class="total-section">
          <span>Total:</span>
          <span class="total-price">€{{ product.price.toFixed(2) }}</span>
        </div>
      </div>

      <div class="shipping-details">
        <h2>Shipping Information</h2>
        <div v-if="isProfileComplete" class="address-card">
          <p>
            <strong>{{ user.name }}</strong>
          </p>
          <p>{{ user.shipping_address }}</p>
          <p>{{ user.shipping_city }}, {{ user.shipping_zip }}</p>
          <p>{{ user.shipping_country }}</p>
          <router-link to="/profile" class="edit-link"
            >Edit Address</router-link
          >
        </div>
        <div v-else class="address-incomplete">
          <p>
            Your shipping information is incomplete. Please update your profile
            before placing an order.
          </p>
          <router-link to="/profile" class="cta-button"
            >Go to Profile</router-link
          >
        </div>
      </div>

      <div class="payment-section">
        <button
          @click="placeOrder"
          class="place-order-button"
          :disabled="!isProfileComplete || isPlacingOrder"
        >
          {{ isPlacingOrder ? "Placing Order..." : "Place Order (Simulation)" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { notifyError } from "../notifications";
import API_BASE_URL from "@/apiConfig";

export default {
  name: "CheckoutView",
  props: {
    designId: {
      type: [String, Number],
      required: true,
    },
  },

  data() {
    return {
      design: null,
      product: null,
      user: null,
      loading: true,
      isPlacingOrder: false,
    };
  },

  computed: {
    isProfileComplete() {
      if (!this.user) return false;
      return (
        this.user.name &&
        this.user.shipping_address &&
        this.user.shipping_city &&
        this.user.shipping_zip &&
        this.user.shipping_country
      );
    },
  },

  async created() {
    try {
      const [designRes, profileRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/designs/${this.designId}`, {
          withCredentials: true,
        }),
        axios.get(`${API_BASE_URL}/api/profile`, { withCredentials: true }), // Correcte backticks
      ]);

      this.design = designRes.data;
      this.user = profileRes.data;

      // We hoeven de producten niet meer apart op te halen, want ze zitten nu in het design object!
      this.product = this.design.product;
    } catch (error) {
      console.error("Error loading checkout data:", error);
      this.$router.push("/my-designs");
    } finally {
      this.loading = false;
    }
  },

  methods: {
    async placeOrder() {
      if (!this.isProfileComplete) return;
      this.isPlacingOrder = true;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/api/orders`, // Correcte backticks
          { design_id: this.design.id },
          { withCredentials: true }
        );
        const newOrder = response.data;
        this.$router.push({
          name: "OrderConfirmation",
          params: { orderId: newOrder.id },
        });
      } catch (error) {
        console.error("Error placing order:", error);
        notifyError(
          error.response?.data?.error ||
            "Could not place the order. Please try again."
        );
      } finally {
        this.isPlacingOrder = false;
      }
    },
  },
};
</script>

<style scoped>
.checkout-page {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
}
.checkout-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}
.order-summary,
.shipping-details {
  background: #fff;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}
h1,
h2 {
  text-align: left;
  margin-top: 0;
}
.product-item {
  display: flex;
  gap: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
}
.product-thumbnail {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}
.product-details h3 {
  margin: 0 0 5px;
}
.product-details p {
  margin: 0;
  color: #666;
}
.price {
  font-weight: bold;
  margin-top: 10px !important;
  color: #333 !important;
}
.total-section {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  font-size: 1.2rem;
  margin-top: 20px;
}
.address-card {
  text-align: left;
  line-height: 1.6;
}
.address-card p {
  margin: 4px 0;
}
.edit-link {
  display: inline-block;
  margin-top: 10px;
  color: #007bff;
  font-weight: bold;
}
.address-incomplete {
  background-color: #fff3cd;
  color: #856404;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ffeeba;
}
.cta-button {
  display: inline-block;
  margin-top: 15px;
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
}
.payment-section {
  margin-top: 20px;
}
.place-order-button {
  width: 100%;
  padding: 18px;
  font-size: 1.2rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}
.place-order-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
