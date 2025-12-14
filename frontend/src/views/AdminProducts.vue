<template>
  <div class="admin-products-page">
    <h1>Admin Dashboard</h1>

    <div class="tabs">
      <button
        :class="{ active: activeTab === 'selected' }"
        @click="activeTab = 'selected'"
      >
        Geselecteerde Producten
      </button>
      <button
        :class="{ active: activeTab === 'all' }"
        @click="activeTab = 'all'"
      >
        Alle Producten
      </button>
    </div>

    <!-- TAB 1: Selected Products (List View) -->
    <div v-if="activeTab === 'selected'" class="tab-content">
      <div v-if="loading" class="loading">Laden...</div>
      <div v-else-if="products.length === 0">Geen producten gevonden.</div>

      <div v-else class="product-list-container">
        <!-- HEADER -->
        <div class="list-header">
          <div class="col-image">Foto</div>
          <div class="col-pid">Product ID</div>
          <div class="col-pname">Printful Naam</div>
          <div class="col-name">Naam</div>
          <div class="col-desc">Beschrijving</div>
          <div class="col-price">Prijs</div>
          <div class="col-link">Link</div>
          <div class="col-actions">Acties</div>
        </div>

        <!-- ROWS -->
        <div
          v-for="product in products"
          :key="product.id"
          class="product-row-wrapper"
        >
          <div class="product-row">
            <div class="col-image">
              <img
                :src="
                  product.product_image_url ||
                  require('@/assets/placeholder.svg')
                "
                width="50"
                @error="$event.target.src = require('@/assets/placeholder.svg')"
              />
            </div>
            <div class="col-pid">{{ product.printful_product_id }}</div>
            <div class="col-pname">
              {{ product.printful_name || "Laden..." }}
            </div>
            <!-- Placeholder as we don't store printful original name in Product model currently -->

            <div class="col-name">
              <input
                v-model="product.name"
                @change="updateProduct(product)"
                class="edit-input"
              />
            </div>

            <div class="col-desc">
              <textarea
                v-model="product.description"
                @change="updateProduct(product)"
                class="edit-input"
                rows="2"
              ></textarea>
            </div>

            <div class="col-price">
              <input
                type="number"
                :value="getProductPrice(product)"
                @change="updateProductPrice(product, $event.target.value)"
                step="0.01"
                class="edit-input price-input"
              />
            </div>

            <div class="col-link">
              <a
                :href="`https://www.printful.com/search?q=${encodeURIComponent(
                  product.printful_name || product.printful_product_id
                )}`"
                target="_blank"
                >Printful (Zoek)</a
              >
            </div>

            <div class="col-actions">
              <button class="btn-toggle" @click="toggleVariants(product.id)">
                {{
                  expandedProductIds.includes(product.id)
                    ? "▲ Verberg"
                    : "▼ Varianten"
                }}
              </button>
              <button class="btn-delete" @click="deleteProduct(product)">
                🗑️
              </button>
            </div>
          </div>

          <!-- VARIANT LIST (Expandable) -->
          <div
            v-if="expandedProductIds.includes(product.id)"
            class="variant-list"
          >
            <div class="variant-header">
              <div class="variant-list-header">
                <div class="v-col-image">Foto</div>
                <div class="v-col-id">Printful ID</div>
                <div class="v-col-color">Kleur</div>
                <div class="v-col-size">Maat</div>
                <div class="v-col-pprice">Inkoop</div>
                <div class="v-col-stock">Voorraad</div>
                <div class="v-col-active">Selectie</div>
              </div>
            </div>

            <div
              v-for="variant in product.variants"
              :key="variant.id"
              class="variant-row"
            >
              <div class="v-col-image">
                <img
                  :src="getVariantImage(variant)"
                  width="30"
                  @error="
                    $event.target.src = require('@/assets/placeholder.svg')
                  "
                />
              </div>
              <div class="v-col-id">{{ variant.printful_variant_id }}</div>
              <div class="v-col-color">
                <span
                  class="color-dot"
                  :style="{ backgroundColor: variant.color_code || '#ccc' }"
                ></span>
                {{ variant.color }}
              </div>
              <div class="v-col-size">{{ variant.size }}</div>
              <div class="v-col-pprice">€{{ variant.printful_price }}</div>
              <div class="v-col-stock">
                {{ variant.in_stock ? "✅" : "❌" }}
              </div>
              <div class="v-col-active">
                <input
                  type="checkbox"
                  :checked="variant.is_active"
                  @change="toggleVariantActive(variant, $event.target.checked)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: All Products (Placeholder) -->
    <!-- TAB 2: All Products (Catalog) -->
    <div v-if="activeTab === 'all'" class="tab-content">
      <div class="catalog-header">
        <h2>Printful Catalogus</h2>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Zoek product..."
          class="search-input"
        />
      </div>

      <div v-if="catalogLoading" class="loading">Catalogus laden...</div>

      <div v-else class="catalog-list">
        <!-- List Header -->
        <div class="list-header catalog-header-row">
          <div class="col-image">Foto</div>
          <div class="col-pid">ID</div>
          <div class="col-pname">Printful Naam</div>
          <div class="col-desc">Printful Beschrijving</div>
          <div class="col-price">Printful Prijs</div>
          <div class="col-link">Printful Link</div>
          <div class="col-actions">Acties</div>
        </div>

        <!-- List Rows -->
        <div
          v-for="item in filteredCatalog"
          :key="item.id"
          class="catalog-row product-row"
        >
          <div class="col-image">
            <img :src="item.image" width="50" alt="" />
          </div>
          <div class="col-pid">{{ item.id }}</div>
          <div class="col-pname">{{ item.title }}</div>
          <div class="col-desc text-muted">
            <span v-if="item.description">{{ item.description }}</span>
            <button v-else @click="fetchDetails(item)" class="btn-info-small">
              ℹ️ Laad Info
            </button>
          </div>
          <div class="col-price text-muted">
            <span v-if="item.price">{{ item.price }}</span>
            <span v-else>-</span>
          </div>
          <div class="col-link">
            <a
              :href="`https://www.printful.com/search?q=${encodeURIComponent(
                item.title
              )}`"
              target="_blank"
              >Link</a
            >
          </div>
          <div class="col-actions">
            <button
              @click="addToShop(item)"
              :disabled="importingId === item.id || isAlreadyInStore(item.id)"
              class="btn-add small"
            >
              {{
                importingId === item.id
                  ? "Bezig..."
                  : isAlreadyInStore(item.id)
                  ? "Toegevoegd"
                  : "Toevoegen"
              }}
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="!catalogLoading && filteredCatalog.length === 0"
        class="empty-state"
      >
        Geen producten gevonden.
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/apiConfig.js";

export default {
  name: "AdminProducts",
  data() {
    return {
      activeTab: "selected",
      products: [],
      loading: false,
      expandedProductIds: [],
      // Catalog Data
      catalog: [],
      catalogLoading: false,
      searchQuery: "",
      importingId: null,
    };
  },
  async created() {
    await this.fetchProducts();
    // Prefetch catalog? Or wait for tab switch?
    // Let's prefetch to be fast
    this.fetchCatalog();
  },
  computed: {
    filteredCatalog() {
      if (!this.searchQuery) return this.catalog;
      const q = this.searchQuery.toLowerCase();
      return this.catalog.filter(
        (item) =>
          item.title.toLowerCase().includes(q) ||
          item.model.toLowerCase().includes(q)
      );
    },
  },
  methods: {
    async fetchProducts() {
      this.loading = true;
      try {
        // Use the new ADMIN endpoint to get inactive variants too
        const response = await axios.get("/api/admin/products");
        this.products = response.data;
      } catch (error) {
        console.error("Failed to fetch products:", error);
      } finally {
        this.loading = false;
      }
    },

    getProductPrice(product) {
      // Display price of first variant as representative
      if (product.variants && product.variants.length > 0) {
        return product.variants[0].price;
      }
      return 0;
    },

    getVariantImage(variant) {
      return variant.image || require("@/assets/placeholder.svg");
    },

    toggleVariants(productId) {
      if (this.expandedProductIds.includes(productId)) {
        this.expandedProductIds = this.expandedProductIds.filter(
          (id) => id !== productId
        );
      } else {
        this.expandedProductIds.push(productId);
      }
    },

    async updateProduct(product) {
      try {
        await axios.put(`/api/products/${product.id}`, {
          name: product.name,
          description: product.description,
        });
        // Feedback via toast could be added here
        console.log("Product updated");
      } catch (error) {
        console.error("Update failed", error);
        alert("Fout bij opslaan product naam");
      }
    },

    async updateProductPrice(product, newPrice) {
      try {
        await axios.put(`/api/products/${product.id}/price`, {
          price: parseFloat(newPrice),
        });
        // We might want to reload products or update local state manually
        // For now, assume success and maybe reload to sync all variants
        await this.fetchProducts();
        console.log("Price updated");
      } catch (error) {
        console.error("Price update failed", error);
        alert("Fout bij opslaan prijs");
      }
    },

    async toggleVariantActive(variant, isActive) {
      try {
        await axios.put(`/api/variants/${variant.id}`, {
          is_active: isActive,
        });
        variant.is_active = isActive; // Optimistic update
      } catch (error) {
        console.error("Variant toggle failed", error);
        // Revert on failure
        variant.is_active = !isActive;
        alert("Fout bij wijzigen status");
      }
    },

    // --- Catalog Methods ---
    async fetchCatalog() {
      this.catalogLoading = true;
      try {
        const response = await axios.get("/api/printful/catalog");
        this.catalog = response.data;
      } catch (error) {
        console.error("Catalog fetch failed", error);
      } finally {
        this.catalogLoading = false;
      }
    },

    isAlreadyInStore(printfulId) {
      return this.products.some((p) => p.printful_product_id === printfulId);
    },

    async addToShop(item) {
      this.importingId = item.id;
      try {
        const response = await axios.post("/api/products/import", {
          printful_id: item.id,
        });
        // Add new product to local list so "Added" state updates and it shows in tab 1
        this.products.push(response.data.product);
        alert(`${item.title} toegevoegd!`);
      } catch (error) {
        console.error("Import failed", error);
        if (error.response && error.response.status === 409) {
          alert("Product bestaat al!");
        } else {
          alert("Er ging iets mis bij het toevoegen.");
        }
      } finally {
        this.importingId = null;
      }
    },
    async deleteProduct(product) {
      if (
        !confirm(
          `Weet je zeker dat je "${product.name}" wilt verwijderen? Dit kan niet ongedaan worden gemaakt.`
        )
      ) {
        return;
      }
      try {
        await axios.delete(`/api/products/${product.id}`);
        // Remove from local list
        this.products = this.products.filter((p) => p.id !== product.id);
      } catch (error) {
        console.error("Delete failed", error);
        alert("Verwijderen mislukt. Mogelijk zijn er bestellingen gekoppeld.");
      }
    },
    async fetchDetails(item) {
      try {
        // Set temporary loading state if desired, or just wait
        const response = await axios.get(`/api/printful/catalog/${item.id}`);
        // Update the item in the catalog array reactively
        // item.description = response.data.description; // Vue 2 caveat: might need Vue.set or assignment
        // Assuming this is Vue 3 or Vue 2 with proper reactivity if item properties exist.
        // But item from catalog API didn't have description.
        // We use this.$set for Vue 2 safety or standard assign.
        // Let's assume standard assignment works if we re-assign property or use spread.

        // Safe Vue 2/3 way:
        const updatedItem = {
          ...item,
          description: response.data.description
            ? response.data.description.substring(0, 50) + "..."
            : "",
          price: response.data.price,
        };
        // Find index and replace to trigger reactivity
        const index = this.catalog.indexOf(item);
        if (index !== -1) {
          this.catalog.splice(index, 1, updatedItem);
        }
      } catch (error) {
        console.error("Fetch details failed", error);
        alert("Kon details niet laden.");
      }
    },
  },
};
</script>

<style scoped>
.admin-products-page {
  padding: 40px;
  max-width: 95%; /* Wider for table */
  margin: 0 auto;
}

.tabs {
  margin-bottom: 30px;
  border-bottom: 2px solid #ddd;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background: none;
  font-size: 1.1rem;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  color: #666;
}

.tabs button.active {
  border-bottom-color: #fc4c02;
  color: #fc4c02;
  font-weight: bold;
}

/* LIST LAYOUT (Grid) */
.list-header,
.product-row {
  display: grid;
  grid-template-columns: 60px 100px 150px 1fr 1fr 100px 80px 120px; /* added description col */
  gap: 15px;
  align-items: center;
  padding: 10px;
}

.list-header {
  font-weight: bold;
  background-color: #f9f9f9;
  border-bottom: 2px solid #eee;
}

.product-row-wrapper {
  background: #fff;
  border-bottom: 1px solid #eee;
  margin-bottom: 5px;
}

/* COLUMNS */
.col-image img {
  border-radius: 4px;
}
.edit-input {
  width: 100%;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-toggle {
  background: #eee;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 0.9rem;
}

/* VARIANT LIST (Child Table) */
.variant-list {
  background-color: #fafafa;
  padding: 10px 20px;
  border-top: 1px solid #eee;
}

.variant-list-header,
.variant-row {
  display: grid;
  grid-template-columns: 50px 80px 120px 60px 80px 80px 80px;
  gap: 10px;
  align-items: center;
  padding: 5px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.9rem;
}

.variant-header {
  font-weight: bold;
  color: #666;
}

.color-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 5px;
  border: 1px solid #ccc;
}

.status-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
}
.status-badge.active {
  background: #d4edda;
  color: #155724;
}
.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

/* CATALOG GRID */
.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.search-input {
  padding: 10px;
  width: 300px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
/* CATALOG LIST */
.catalog-header-row,
.catalog-row {
  display: grid;
  grid-template-columns: 60px 80px 1fr 1fr 100px 80px 120px;
  gap: 15px;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
}
.catalog-header-row {
  font-weight: bold;
  background: #f9f9f9;
  border-bottom: 2px solid #ddd;
}
.catalog-row img {
  object-fit: cover;
  border-radius: 4px;
}
.text-muted {
  color: #999;
  font-style: italic;
  font-size: 0.9em;
}
.btn-add.small {
  padding: 5px 10px;
  font-size: 0.85rem;
}
.btn-delete {
  background: #dc3545;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 5px;
}
.btn-delete:hover {
  background: #c82333;
}
.btn-info-small {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
  cursor: pointer;
}
/* Removed old card styles */
</style>
