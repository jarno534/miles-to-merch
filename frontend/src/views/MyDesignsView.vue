<template>
  <div class="my-designs-page">
    <h1>My Designs</h1>
    <div v-if="loading" class="loading">Loading your designs...</div>
    <div v-else-if="designs.length === 0" class="no-designs">
      <p>You haven't saved any designs yet.</p>
      <router-link to="/" class="cta-button">Start Creating</router-link>
    </div>
    <div v-else class="designs-grid">
      <div v-for="design in designs" :key="design.id" class="design-card">
        <div class="card-header">
          <h3>{{ design.name }}</h3>
          <span>Saved on {{ formatDate(design.created_at) }}</span>
        </div>
        <div class="card-actions">
          <button @click="orderDesign(design.id)" class="action-button order">
            Order
          </button>
          <button @click="editDesign(design)" class="action-button edit">
            Edit
          </button>
          <button @click="deleteDesign(design.id)" class="action-button delete">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "MyDesignsView",
  data() {
    return {
      designs: [],
      loading: true,
    };
  },
  async created() {
    await this.fetchDesigns();
  },
  methods: {
    orderDesign(designId) {
      this.$router.push({ name: "Checkout", params: { designId: designId } });
    },
    async fetchDesigns() {
      this.loading = true;
      try {
        const response = await axios.get("http://localhost:5000/api/designs", {
          withCredentials: true,
        });
        this.designs = response.data;
      } catch (error) {
        console.error("Error fetching designs:", error);
        if (error.response && error.response.status === 401) {
          this.$router.push({ name: "home" });
        }
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
    editDesign(design) {
      // Navigate to the design page to edit this specific design
      // Note: We need to get the activityId and productId from the saved design data
      const activityId = design.design_data.activityId;
      const productId = design.product_id;

      this.$router.push({
        name: "Design",
        params: { productId, activityId },
        query: { design_id: design.id }, // We pass the design ID as a query parameter
      });
    },
    async deleteDesign(designId) {
      if (!confirm("Are you sure you want to delete this design?")) {
        return;
      }
      try {
        await axios.delete(`http://localhost:5000/api/designs/${designId}`, {
          withCredentials: true,
        });
        // Refresh the list after deleting
        await this.fetchDesigns();
      } catch (error) {
        console.error("Error deleting design:", error);
        alert("Could not delete the design. Please try again.");
      }
    },
  },
};
</script>

<style scoped>
.my-designs-page {
  max-width: 1000px;
  margin: 40px auto;
  padding: 20px;
}
.loading,
.no-designs {
  text-align: center;
  margin-top: 50px;
  color: #666;
}
.no-designs p {
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
  transition: background-color 0.2s;
}
.cta-button:hover {
  background-color: #e24300;
}
.designs-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}
.design-card {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header h3 {
  margin: 0 0 5px;
}
.card-header span {
  font-size: 0.9em;
  color: #777;
}
.action-button {
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  margin-left: 10px;
  transition: background-color 0.2s;
}
.action-button.edit {
  background-color: #007bff;
  color: white;
}
.action-button.edit:hover {
  background-color: #0056b3;
}
.action-button.delete {
  background-color: #dc3545;
  color: white;
}
.action-button.delete:hover {
  background-color: #c82333;
}
.action-button.order {
  background-color: #28a745;
  color: white;
}
.action-button.order:hover {
  background-color: #218838;
}
</style>
