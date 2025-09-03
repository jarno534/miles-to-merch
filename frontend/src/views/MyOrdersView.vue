<template>
  <div class="my-orders-page">
    <h1>My Orders</h1>
    <SpinnerComponent v-if="loading" text="Loading your orders..." />
    <div v-else-if="orders.length > 0" class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <img
          :src="order.product_image_url"
          :alt="order.product_name"
          class="product-thumbnail"
        />
        <div class="order-info">
          <h3>{{ order.product_name }}</h3>
          <p>Design: "{{ order.design_name || "My Design" }}"</p>
          <p>
            Order #{{ order.id }} - Placed on {{ formatDate(order.order_date) }}
          </p>
        </div>
        <div class="order-details">
          <p class="price">€{{ order.total_price.toFixed(2) }}</p>
          <span class="status">{{ order.order_status }}</span>
        </div>
      </div>
    </div>
    <div v-else class="no-orders">
      <p>You haven't placed any orders yet.</p>
      <router-link to="/" class="cta-button">Start Designing</router-link>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SpinnerComponent from "@/components/SpinnerComponent.vue";
import API_BASE_URL from "@/apiConfig";

export default {
  name: "MyOrdersView",
  components: { SpinnerComponent },
  data() {
    return {
      orders: [],
      loading: true,
    };
  },

  async created() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/orders`, {
        withCredentials: true,
      });
      this.orders = response.data;
    } catch (error) {
      console.error("Error fetching orders:", error);
    } finally {
      this.loading = false;
    }
  },

  methods: {
    formatDate(dateString) {
      const options = { year: "numeric", month: "long", day: "numeric" };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
  },
};
</script>

<style scoped>
.my-orders-page {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 40px;
}

.orders-list {
  display: grid;
  gap: 20px;
}

.order-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.product-thumbnail {
  width: 90px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.order-info {
  flex-grow: 1;
  text-align: left;
}

.order-info h3,
.order-info p {
  margin: 0 0 5px;
}

.order-info p {
  font-size: 0.9em;
  color: #666;
}

.order-details {
  text-align: right;
}

.price {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.status {
  background-color: #e9ecef;
  color: #495057;
  padding: 4px 8px;
  border-radius: 5px;
  font-size: 0.8em;
  font-weight: bold;
}

.no-orders {
  text-align: center;
  margin-top: 50px;
  color: #666;
}

.cta-button {
  display: inline-block;
  margin-top: 20px;
  background-color: #007bff;
  color: white;
  padding: 12px 25px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
}
</style>
