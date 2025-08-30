<template>
  <div class="confirmation-page">
    <SpinnerComponent
      v-if="loading"
      text="Loading your order confirmation..."
    />
    <div v-else-if="order" class="confirmation-container">
      <div class="success-icon">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
          />
        </svg>
      </div>
      <h1>Thank You For Your Order!</h1>
      <p class="subtitle">
        Your order #{{ order.id }} has been placed successfully.
      </p>

      <div class="order-summary-card">
        <h3>Order Summary</h3>
        <div class="product-item">
          <img
            :src="order.product_image_url"
            :alt="order.product_name"
            class="product-thumbnail"
          />
          <div class="product-details">
            <h4>{{ order.product_name }}</h4>
            <p>Custom design: "{{ order.design_name }}"</p>
          </div>
          <p class="price">€{{ order.total_price.toFixed(2) }}</p>
        </div>
      </div>

      <div class="next-steps">
        <p>You will receive an email confirmation shortly.</p>
        <router-link to="/my-orders" class="cta-button"
          >View My Orders</router-link
        >
        <router-link to="/" class="secondary-link"
          >Continue Shopping</router-link
        >
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SpinnerComponent from "@/components/SpinnerComponent.vue";

export default {
  name: "OrderConfirmationView",
  components: { SpinnerComponent },
  props: {
    orderId: {
      type: [String, Number],
      required: true,
    },
  },
  data() {
    return {
      order: null,
      loading: true,
    };
  },
  async created() {
    try {
      // Deze API call haalt de details van de zojuist gemaakte bestelling op
      const response = await axios.get(
        `http://localhost:5000/api/orders/${this.orderId}`,
        {
          withCredentials: true,
        }
      );
      this.order = response.data;
    } catch (error) {
      console.error("Error fetching order confirmation:", error);
      this.$router.push("/my-orders");
    } finally {
      this.loading = false;
    }
  },
};
</script>

<style scoped>
/* Deze stijlen zijn een mix van jouw code en een paar verbeteringen */
.confirmation-page {
  max-width: 700px;
  margin: 40px auto;
  padding: 20px;
  text-align: center;
}
.success-icon svg {
  width: 80px;
  height: 80px;
  color: #28a745;
  margin-bottom: 20px;
}
h1 {
  margin: 0 0 10px;
}
.subtitle {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 30px;
}
.order-summary-card {
  background: #fff;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  text-align: left;
  margin-bottom: 30px;
}
.product-item {
  display: flex;
  gap: 20px;
  align-items: center;
}
.product-thumbnail {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
}
.product-details {
  flex-grow: 1;
}
.product-details h4,
.product-details p {
  margin: 0;
}
.price {
  font-weight: bold;
  font-size: 1.1rem;
}
.next-steps p {
  margin-bottom: 20px;
}
.cta-button {
  display: inline-block;
  background-color: #007bff;
  color: white;
  padding: 12px 25px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  margin-right: 15px;
}
.secondary-link {
  color: #007bff;
  font-weight: bold;
}
</style>
