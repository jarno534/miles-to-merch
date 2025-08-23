<template>
  <div class="product-detail-page">
    <SpinnerComponent v-if="loading" />
    <div v-if="product" class="product-container">
      <div class="product-image-container">
        <img
          :src="product.image_url"
          :alt="product.name"
          class="product-image"
        />
      </div>
      <div class="product-info-container">
        <h1 class="product-name">{{ product.name }}</h1>
        <p class="product-price">€{{ product.price.toFixed(2) }}</p>
        <p class="product-description">{{ product.description }}</p>

        <div class="product-specs">
          <h2>Product Details</h2>
          <ul>
            <li><strong>Material:</strong> 100% organic ring-spun cotton</li>
            <li><strong>Weight:</strong> 180 g/m²</li>
            <li><strong>Fit:</strong> Medium fit, unisex</li>
            <li>
              <strong>Available Colors:</strong> White, Black, Navy, Heather
              Grey
            </li>
          </ul>
        </div>

        <button @click="startDesigning" class="design-button">
          Start Designing
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SpinnerComponent from "@/components/SpinnerComponent.vue";

export default {
  name: "ProductDetailView",
  components: { SpinnerComponent },
  props: {
    productId: {
      type: [String, Number],
      required: true,
    },
  },
  data() {
    return {
      product: null,
      loading: true,
    };
  },
  async created() {
    try {
      const response = await axios.get(
        `http://localhost:5000/api/products/${this.productId}`
      );
      this.product = response.data;
    } catch (error) {
      console.error("Error fetching product details:", error);
      this.$router.push({ name: "home" });
    } finally {
      this.loading = false;
    }
  },
  methods: {
    startDesigning() {
      this.$router.push({
        name: "StartDesign",
        params: { productId: this.productId },
      });
    },
  },
};
</script>

<style scoped>
.product-detail-page {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  min-height: 100vh;
  background-color: #f0f2f5;
}
.product-container {
  display: flex;
  flex-direction: row;
  gap: 40px;
  max-width: 1100px;
  width: 100%;
  background: #fff;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}
.product-image-container {
  flex: 1;
}
.product-image {
  width: 100%;
  border-radius: 10px;
}
.product-info-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.product-name {
  font-size: 2.5rem;
  margin: 0 0 10px;
}
.product-price {
  font-size: 1.8rem;
  font-weight: bold;
  color: #fc4c02;
  margin-bottom: 20px;
}
.product-description {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #555;
  margin-bottom: 30px;
}
.product-specs {
  margin-bottom: 30px;
}
.product-specs h2 {
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}
.product-specs ul {
  list-style: none;
  padding: 0;
}
.product-specs li {
  margin-bottom: 8px;
  color: #444;
}
.design-button {
  background-color: #fc4c02;
  color: white;
  border: none;
  padding: 15px 25px;
  border-radius: 8px;
  font-weight: bold;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: auto;
}
.design-button:hover {
  background-color: #e24300;
}
</style>
