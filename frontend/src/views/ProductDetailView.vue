<template>
  <div class="product-detail-page">
    <SpinnerComponent v-if="loading" text="Loading product details..." />
    <div v-else-if="product" class="product-container">
      <div class="product-image-container">
        <img
          :src="displayImageUrl"
          :alt="product.name"
          class="product-image"
          @error="handleImageError"
        />
      </div>
      <div class="product-info-container">
        <h1 class="product-name">{{ product.name }}</h1>
        <p class="product-price">€{{ displayPrice.toFixed(2) }}</p>
        <p class="product-description">{{ product.description }}</p>

        <div v-if="availableColors.length > 0" class="options-section">
          <h2>
            Color:
            <span class="selected-option">{{
              selectedColor || "Select a color"
            }}</span>
          </h2>
          <div class="color-swatches">
            <button
              v-for="color in availableColors"
              :key="color.name"
              class="color-swatch"
              :class="{ active: selectedColor === color.name }"
              @click="selectColor(color.name)"
              :title="color.name"
              :style="{ backgroundColor: color.code }"
            ></button>
          </div>
        </div>

        <div v-if="availableSizes.length > 0" class="options-section">
          <h2>
            Size:
            <span class="selected-option">{{
              selectedSize || "Select a size"
            }}</span>
          </h2>
          <div class="size-buttons">
            <button
              v-for="size in availableSizes"
              :key="size"
              class="size-button"
              :class="{ active: selectedSize === size }"
              @click="selectSize(size)"
            >
              {{ size }}
            </button>
          </div>
        </div>

        <button
          @click="startDesigning"
          class="design-button"
          :disabled="!selectedVariant"
        >
          Customize Design
        </button>
        <p
          v-if="product.variants.length > 0 && !selectedVariant"
          class="selection-prompt"
        >
          Please select a color and size to continue.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/apiConfig.js";
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
      selectedColor: null,
      selectedSize: null,
    };
  },

  computed: {
    displayImageUrl() {
      // 1. Try to find a variant-specific match
      if (this.selectedColor && this.product?.variants) {
        const variantForColor = this.product.variants.find(
          (v) => v.color === this.selectedColor
        );
        if (variantForColor) {
          console.log("Variant Data:", variantForColor); // Debug log
          return this.getImageUrl(variantForColor);
        }
      }

      // 2. Fallback: First available variant
      if (this.product?.variants?.length > 0) {
        return this.getImageUrl(this.product.variants[0]);
      }

      // 3. Fallback: Product-level image or placeholder
      return (
        this.product?.product_image_url || require("@/assets/placeholder.svg")
      ); // Ensure you have a placeholder or handle this path
    },

    displayPrice() {
      if (this.selectedVariant) {
        return this.selectedVariant.price;
      }
      return this.product?.variants[0]?.price || 0;
    },

    availableColors() {
      if (!this.product?.variants) return [];
      const colors = {};
      this.product.variants.forEach((v) => {
        if (!colors[v.color]) {
          colors[v.color] = { name: v.color, code: v.color_code || "#ffffff" };
        }
      });
      return Object.values(colors);
    },

    availableSizes() {
      if (!this.selectedColor || !this.product?.variants) return [];
      return this.product.variants
        .filter((v) => v.color === this.selectedColor)
        .map((v) => v.size);
    },

    selectedVariant() {
      if (!this.selectedColor || !this.selectedSize || !this.product?.variants)
        return null;
      return (
        this.product.variants.find(
          (v) => v.color === this.selectedColor && v.size === this.selectedSize
        ) || null
      );
    },
  },

  async created() {
    try {
      const response = await axios.get(`/api/products/${this.productId}`);
      this.product = response.data;
    } catch (error) {
      console.error("Error fetching product data:", error);
    } finally {
      this.loading = false;
    }
  },

  methods: {
    getImageUrl(variant) {
      if (!variant) return "";
      if (variant.image_base_path) {
        const filename =
          variant.image_base_path === "mug" ? "center.jpg" : "front.jpg";
        return `/${variant.image_base_path}/${filename}`;
      }
      return variant.image || "";
    },

    selectColor(colorName) {
      this.selectedColor = colorName;
      if (!this.availableSizes.includes(this.selectedSize)) {
        this.selectedSize = null;
      }
    },

    selectSize(size) {
      this.selectedSize = size;
    },

    getColorSwatchUrl(colorName) {
      const variant = this.product.variants.find((v) => v.color === colorName);
      return this.getImageUrl(variant);
    },

    startDesigning() {
      if (!this.selectedVariant) return;
      localStorage.setItem("selectedVariantId", this.selectedVariant.id);
      localStorage.setItem("selectedProductId", this.productId);
      this.$router.push({
        name: "StartDesign",
        params: { productId: this.productId },
      });
    },

    handleImageError(e) {
      console.warn("Image failed to load:", e.target.src);
      // Prevent infinite loop if placeholder also fails
      if (!e.target.src.includes("placeholder")) {
        e.target.src = require("@/assets/placeholder.svg"); // Make sure this asset exists or use a web url
      }
    },
  },
};
</script>

<style scoped>
.product-detail-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
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
  position: sticky;
  top: 40px;
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
  text-align: left;
}

.product-price {
  font-size: 1.8rem;
  font-weight: bold;
  color: #fc4c02;
  margin-bottom: 20px;
  text-align: left;
}

.product-description {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #555;
  margin-bottom: 30px;
  text-align: left;
}

.options-section {
  margin-bottom: 25px;
  text-align: left;
}

.options-section h2 {
  font-size: 1.2rem;
  margin: 0 0 10px;
  color: #333;
}

.selected-option {
  font-weight: normal;
  color: #666;
}

.color-swatches,
.size-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.color-swatch {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  border: 1px solid #ccc;
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s;
  padding: 2px;
  background-color: #fff;
}

.color-swatch img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.color-swatch.active {
  border-color: #fc4c02;
  transform: scale(1.15);
}

.size-button {
  padding: 8px 15px;
  border: 2px solid #ccc;
  background: #fff;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.size-button.active {
  background-color: #fc4c02;
  color: white;
  border-color: #fc4c02;
}

.design-button {
  background-color: #28a745;
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

.design-button:hover:not(:disabled) {
  background-color: #218838;
}

.design-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.selection-prompt {
  text-align: center;
  color: #888;
  margin-top: 10px;
}
</style>
