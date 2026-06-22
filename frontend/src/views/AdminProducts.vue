<template>
  <div class="admin-products-page">
    <h1>Admin Dashboard</h1>

    <div class="tabs">
      <button
        :class="{ active: activeTab === 'selected' }"
        @click="activeTab = 'selected'"
      >
        Producten
      </button>
      <button
        :class="{ active: activeTab === 'all' }"
        @click="activeTab = 'all'"
      >
        Printful Catalogus
      </button>
      <button :class="{ active: activeTab === 'users' }" @click="fetchUsers">
        Gebruikers
      </button>
      <button
        :class="{ active: activeTab === 'designs' }"
        @click="fetchDesigns"
      >
        Ontwerpen
      </button>
      <button :class="{ active: activeTab === 'orders' }" @click="fetchOrders">
        Bestellingen
      </button>
      <button
        :class="{ active: activeTab === 'advanced' }"
        @click="activeTab = 'advanced'"
      >
        Geavanceerd Systeem
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
              <router-link
                :to="'/admin/product/' + product.id + '/canvas'"
                class="btn-info-small"
                style="margin-left: 5px; padding: 5px"
                >Edit Canvas</router-link
              >
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

    <!-- TAB 3: Users -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <h2>Gebruikers</h2>
      <div v-if="usersLoading" class="loading">Laden...</div>
      <table v-else class="simple-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Naam</th>
            <th>Email</th>
            <th>Strava</th>
            <th>Locatie</th>
            <th>Ontwerpen</th>
            <th>Bestellingen</th>
            <th>Admin?</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in usersList" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.name || "Onbekend" }}</td>
            <td>{{ u.email || "-" }}</td>
            <td>{{ u.strava_name || "-" }} ({{ u.strava_id || "-" }})</td>
            <td>
              {{ u.shipping_city || "Onbekend" }},
              {{ u.shipping_country || "" }}
            </td>
            <td>{{ u.created_designs }}</td>
            <td>{{ u.orders_count }}</td>
            <td>{{ u.is_admin ? "Ja" : "Nee" }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- TAB: Designs -->
    <div v-if="activeTab === 'designs'" class="tab-content">
      <h2>Ontwerpen (Designs) van Gebruikers</h2>
      <div v-if="designsLoading" class="loading">Laden...</div>
      <table v-else class="simple-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Datum</th>
            <th>Naam Ontwerp</th>
            <th>Gebruiker</th>
            <th>Product</th>
            <th>Voorbeeld</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in designsList" :key="d.id">
            <td>{{ d.id }}</td>
            <td>{{ new Date(d.created_at).toLocaleString() }}</td>
            <td>{{ d.name }}</td>
            <td>{{ d.user_name }} ({{ d.user_email }})</td>
            <td>{{ d.product_id }} / Variant {{ d.variant_id }}</td>
            <td>
              <img
                v-if="d.preview_urls && d.preview_urls.front"
                :src="d.preview_urls.front"
                width="50"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- TAB 4: Orders -->
    <div v-if="activeTab === 'orders'" class="tab-content">
      <h2>Bestellingen</h2>
      <div v-if="ordersLoading" class="loading">Laden...</div>
      <table v-else class="simple-table">
        <thead>
          <tr>
            <th>Bestelling ID</th>
            <th>Datum</th>
            <th>Gebruiker</th>
            <th>Status</th>
            <th>Printful ID</th>
            <th>Totaal</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in ordersList" :key="o.id">
            <td>#{{ o.id }}</td>
            <td>{{ new Date(o.order_date).toLocaleString() }}</td>
            <td>{{ o.shipping_name || o.user_email }}</td>
            <td>{{ o.order_status }}</td>
            <td>{{ o.printful_order_id || "Nog niet" }}</td>
            <td>€{{ o.total_price }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- TAB 5: Advanced System -->
    <div v-if="activeTab === 'advanced'" class="tab-content advanced-tab">
      <h2>Geavanceerd Systeem Beheer</h2>
      <p>
        Het systeem heeft een complete backend administratie tool waar je
        <strong>álles</strong> kunt aanpassen: gebruikers, orders, varianten per
        maat, ruwe json instellingen, enzovoorts.
      </p>
      <div class="warning-box">
        <strong>Let op:</strong> Als het scherm leeg is of je een "Welcome"
        bericht ziet, komt dit doordat je browser cookies blokkeert tussen de
        frontend en de backend. <br /><br />
        Oplossing: Ga rechtstreeks naar de backend via onderstaande knop. Omdat
        het een aparte omgeving is, moet je daar eenmalig opnieuw inloggen met
        je admin e-mail via <strong>/auth/login</strong> voordat je naar
        <strong>/admin</strong> kunt.
      </div>
      <a
        :href="backendAdminUrl"
        target="_blank"
        class="btn btn-primary btn-large"
      >
        Open het geavanceerde paneel (Nieuw tabblad)
      </a>
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

      // Users, Designs & Orders
      usersList: [],
      usersLoading: false,
      ordersList: [],
      ordersLoading: false,
      designsList: [],
      designsLoading: false,
    };
  },
  async created() {
    await this.fetchProducts();
    // Prefetch catalog? Or wait for tab switch?
    // Let's prefetch to be fast
    this.fetchCatalog();
  },
  computed: {
    backendAdminUrl() {
      const baseUrl =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";
      return baseUrl + "/admin";
    },
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
    async fetchUsers() {
      this.activeTab = "users";
      this.usersLoading = true;
      try {
        const response = await axios.get("/api/admin/users");
        this.usersList = response.data;
      } catch (error) {
        console.error("Fetch users failed", error);
      } finally {
        this.usersLoading = false;
      }
    },
    async fetchOrders() {
      this.activeTab = "orders";
      this.ordersLoading = true;
      try {
        const response = await axios.get("/api/admin/orders");
        this.ordersList = response.data;
      } catch (error) {
        console.error("Fetch orders failed", error);
      } finally {
        this.ordersLoading = false;
      }
    },
    async fetchDesigns() {
      this.activeTab = "designs";
      this.designsLoading = true;
      try {
        const response = await axios.get("/api/admin/designs");
        this.designsList = response.data;
      } catch (error) {
        console.error("Fetch designs failed", error);
      } finally {
        this.designsLoading = false;
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

/* NEW TABS CSS */
.simple-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}
.simple-table th,
.simple-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
.simple-table th {
  background-color: #f2f2f2;
}
.advanced-tab {
  text-align: center;
  padding: 50px;
}
.warning-box {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
  padding: 15px;
  border-radius: 5px;
  margin-top: 20px;
  text-align: left;
}
.btn-large {
  display: inline-block;
  margin-top: 20px;
  padding: 15px 30px;
  font-size: 1.2rem;
  background-color: #fc4c02;
  color: white;
  text-decoration: none;
  border-radius: 5px;
}
.btn-large:hover {
  background-color: #e34402;
}
/* Removed old card styles */
</style>
