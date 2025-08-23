<template>
  <div class="my-orders-page">
    <h1>My Orders</h1>
    <SpinnerComponent v-if="loading" text="Loading your order history..." />
    <div v-else-if="orders.length === 0" class="no-orders">
      <p>You haven't placed any orders yet.</p>
      <router-link to="/my-designs" class="cta-button"
        >View My Designs</router-link
      >
    </div>

    <div v-else class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <div>
            <span class="order-id">Order #{{ order.id }}</span>
            <span class="order-date"
              >Placed on {{ formatDate(order.order_date) }}</span
            >
          </div>
          <span class="order-status">{{ order.order_status }}</span>
        </div>
        <div class="order-body">
          <img
            :src="order.product_image_url"
            :alt="order.product_name"
            class="product-thumbnail"
          />
          <div class="product-details">
            <h4>{{ order.product_name }}</h4>
            <p>Total: €{{ order.total_price.toFixed(2) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { auth } from "../auth";
import SpinnerComponent from "@/components/SpinnerComponent.vue";

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
    if (!auth.isLoggedIn) {
      this.$router.push("/login");
      return;
    }
    await this.fetchOrders();
  },
  methods: {
    async fetchOrders() {
      this.loading = true;
      try {
        const response = await axios.get("http://localhost:5000/api/orders", {
          withCredentials: true,
        });
        this.orders = response.data;

        // DE AUTOMATISCHE REDIRECT IS HIER VERWIJDERD
      } catch (error) {
        console.error("Failed to fetch orders:", error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    },
  },
};
</script>

<style scoped>
.my-orders-page {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
}
.loading,
.no-orders {
  text-align: center;
  margin-top: 50px;
  color: #666;
}
.no-orders p {
  font-size: 1.2rem;
  margin-bottom: 20px;
}
.cta-button {
  background-color: #fc4c02;
  color: white;
  padding: 12px 25px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
}
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.order-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
  padding: 15px 20px;
  border-bottom: 1px solid #e9ecef;
}
.order-id {
  font-weight: bold;
  font-size: 1.1rem;
  margin-right: 15px;
}
.order-date {
  color: #6c757d;
  font-size: 0.9rem;
}
.order-status {
  background-color: #ffc107;
  color: #333;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: bold;
}
.order-body {
  display: flex;
  align-items: center;
  padding: 20px;
  gap: 20px;
}
.product-thumbnail {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
}
.product-details h4 {
  margin: 0 0 5px;
}
.product-details p {
  margin: 0;
}
</style>
