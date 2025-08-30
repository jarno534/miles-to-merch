<template>
  <div class="product-detail-page">
    <SpinnerComponent v-if="loading" text="Loading product details..." />
    <div v-if="product" class="product-container">
      <div class="product-image-container">
        <img :src="displayImageUrl" :alt="product.name" class="product-image" />
      </div>
      <div class="product-info-container">
        <h1 class="product-name">{{ product.name }}</h1>
        <p class="product-price">€{{ product.price.toFixed(2) }}</p>
        <p class="product-description">{{ product.description }}</p>

        <div v-if="availableColors.length > 0" class="options-section">
          <h2>
            Color: <span class="selected-option">{{ selectedColor }}</span>
          </h2>
          <div class="color-swatches">
            <button
              v-for="color in availableColors"
              :key="color.name"
              class="color-swatch"
              :style="{ backgroundColor: color.code }"
              :class="{ active: selectedColor === color.name }"
              @click="selectColor(color.name)"
              :title="color.name"
            ></button>
          </div>
        </div>

        <div v-if="availableSizes.length > 0" class="options-section">
          <h2>
            Size: <span class="selected-option">{{ selectedSize }}</span>
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
          :disabled="!isReadyToDesign"
        >
          Start Designing
        </button>
        <p
          v-if="variants.length > 0 && !isReadyToDesign"
          class="selection-prompt"
        >
          Please select a color and size.
        </p>
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
      variants: [],
      printfulProductDetails: null,
      selectedColor: null,
      selectedSize: null,
      selectedMockupUrl: null,
      selectedVariantId: null,
    };
  },
  computed: {
    displayImageUrl() {
      if (this.selectedMockupUrl) {
        return this.selectedMockupUrl;
      }
      if (this.product && this.product.print_areas) {
        const firstAreaKey = Object.keys(this.product.print_areas)[0];
        if (firstAreaKey) {
          return this.product.print_areas[firstAreaKey].image_url;
        }
      }
      return "";
    },

    availableColors() {
      if (!this.variants) return [];

      const curatedColorNames = [
        "White",
        "Black",
        "Navy",
        "Athletic Heather",
        "Red",
        "Royal Blue",
        "Kelly",
        "Asphalt",
      ];

      const uniqueColors = new Map();
      this.variants.forEach((v) => {
        if (
          v.color &&
          v.color_code &&
          curatedColorNames.includes(v.color) &&
          !uniqueColors.has(v.color)
        ) {
          uniqueColors.set(v.color, v.color_code);
        }
      });

      const sortedColorArray = Array.from(uniqueColors, ([name, code]) => ({
        name,
        code,
      })).sort(
        (a, b) =>
          curatedColorNames.indexOf(a.name) - curatedColorNames.indexOf(b.name)
      );

      return sortedColorArray;
    },

    availableSizes() {
      if (!this.selectedColor || !this.variants) return [];
      return this.variants
        .filter((v) => v.color === this.selectedColor)
        .map((v) => v.size);
    },

    selectedVariant() {
      if (!this.selectedColor || !this.selectedSize || !this.variants)
        return null;
      return (
        this.variants.find(
          (v) => v.color === this.selectedColor && v.size === this.selectedSize
        ) || null
      );
    },

    isReadyToDesign() {
      if (!this.product) {
        return false;
      }
      if (!this.product.printful_product_id || this.variants.length === 0) {
        return true;
      }
      return !!this.selectedVariant;
    },
  },

  async created() {
    try {
      const productRes = await axios.get(
        `http://localhost:5000/api/products/${this.productId}`
      );
      this.product = productRes.data;

      if (this.product.printful_product_id) {
        const detailsRes = await axios.get(
          `http://localhost:5000/api/products/${this.productId}/printful-details`
        );
        this.printfulProductDetails = detailsRes.data;
        this.variants = detailsRes.data.variants;
      }
    } catch (error) {
      console.error("Error fetching product data:", error);
      this.$router.push("/");
    } finally {
      this.loading = false;
    }
  },

  methods: {
    selectColor(colorName) {
      this.selectedColor = colorName;
      if (!this.availableSizes.includes(this.selectedSize)) {
        this.selectedSize = null;
      }

      const firstVariantOfColor = this.variants.find(
        (v) => v.color === colorName
      );

      if (firstVariantOfColor && firstVariantOfColor.image) {
        this.selectedMockupUrl = firstVariantOfColor.image;
      }
    },

    selectSize(size) {
      this.selectedSize = size;
      const variant = this.variants.find(
        (v) => v.color === this.selectedColor && v.size === size
      );
      if (variant) {
        this.selectedVariantId = variant.id;
      }
    },

    startDesigning() {
      if (!this.isReadyToDesign) return;

      localStorage.setItem("selectedVariantId", this.selectedVariantId);
      localStorage.setItem("selectedProductId", this.productId);

      if (this.printfulProductDetails) {
        localStorage.setItem(
          "editorProductData",
          JSON.stringify(this.printfulProductDetails)
        );
      }

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
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid #ccc;
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s;
}
.color-swatch.active {
  border-color: #fc4c02;
  transform: scale(1.15);
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
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
