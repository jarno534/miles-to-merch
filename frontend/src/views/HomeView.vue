<template>
  <div class="products-page">
    <div class="header">
      <p>Choose your favorite item and immortalize your achievement.</p>
    </div>
    <SpinnerComponent v-if="loading" text="Loading products..." />
    <div v-else class="product-grid">
      <div
        v-for="product in products"
        :key="product.id"
        class="product-card"
        @click="selectProduct(product.id)"
      >
        <img
          :src="product.product_image_url || product.variants[0]?.image"
          :alt="product.name"
          class="product-image"
        />
        <div class="product-info">
          <h2 class="product-name">{{ product.name }}</h2>
          <p class="product-description">{{ product.description }}</p>
          <div class="product-footer">
            <span class="product-price" v-if="product.variants.length > 0">
              From €{{ product.variants[0].price.toFixed(2) }}
            </span>
            <button class="details-button">View Options</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/apiConfig.js";
import SpinnerComponent from "@/components/SpinnerComponent.vue";

export default {
  name: "HomeView",
  components: { SpinnerComponent },
  data() {
    return {
      products: [],
      loading: true,
      preselectedActivityId: null,
    };
  },

  created() {
    this.preselectedActivityId = localStorage.getItem("selectedActivityId");
    this.fetchProducts();
  },

  methods: {
    async fetchProducts() {
      try {
        const response = await axios.get("/api/products");
        this.products = response.data;
      } catch (error) {
        console.error("Error fetching products:", error);
      } finally {
        this.loading = false;
      }
    },

    selectProduct(productId) {
      if (this.preselectedActivityId) {
        this.$router.push({
          name: "Design",
          params: {
            productId: productId,
            activityId: this.preselectedActivityId,
          },
        });
        localStorage.removeItem("selectedActivityId");
      } else {
        this.$router.push({
          name: "ProductDetail",
          params: { productId: productId },
        });
      }
    },
  },
};
</script>

<style scoped>
.products-page {
  padding: 40px 20px;
  text-align: center;
  background-color: #f0f2f5;
  min-height: 100vh;
}
.header {
  margin-bottom: 40px;
}
.header h1 {
  font-size: 2.5rem;
  color: #333;
}
.header p {
  font-size: 1.2rem;
  color: #666;
}
.home-logo {
  max-width: 80%;
  height: auto;
  max-height: 150px; /* Adjust as needed */
  margin-bottom: 20px;
}
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}
.product-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
}
.product-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}
.product-image {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: contain;
  background-color: #fff;
}
.product-info {
  padding: 20px;
  text-align: left;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.product-name {
  margin: 0 0 10px;
  font-size: 1.4em;
  color: #333;
}
.product-description {
  margin: 0 0 15px;
  color: #666;
  flex-grow: 1;
}
.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}
.product-price {
  font-size: 1.2em;
  font-weight: bold;
  color: #333;
}
.details-button {
  background-color: #fc4c02;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s, background-color 0.2s, box-shadow 0.2s;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.details-button:hover {
  background-color: #e24300;
}
.loading {
  font-size: 1.2rem;
  color: #666;
}
</style>
