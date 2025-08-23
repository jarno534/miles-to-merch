<template>
  <div class="my-designs-page">
    <h1>My Designs</h1>
    <SpinnerComponent v-if="loading" text="Loading your designs..." />
    <div v-else-if="designs.length === 0" class="no-designs">
      <p>You haven't saved any designs yet.</p>
      <router-link to="/" class="cta-button">Start Creating</router-link>
    </div>
    <div v-else class="designs-grid">
      <div v-for="design in designs" :key="design.id" class="design-card">
        <div class="card-header">
          <div
            class="design-title"
            @click="editDesignName(design)"
            title="Edit name"
          >
            <h3>{{ design.name }}</h3>
            <span class="edit-icon">✏️</span>
          </div>
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
import { notifySuccess, notifyError } from "../notifications";
import SpinnerComponent from "@/components/SpinnerComponent.vue";

export default {
  name: "MyDesignsView",
  components: { SpinnerComponent },
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
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    editDesign(design) {
      // Navigate to the design page to edit this specific design
      // Note: We need to get the activityId and productId from the saved design data
      const activityId = design.design_data.activityId;
      const productId = design.product_id;

      if (!activityId) {
        alert(
          "Error: Could not find the original activity for this design. Cannot edit."
        );
        return;
      }

      this.$router.push({
        name: "Design",
        params: { productId, activityId },
        query: { design_id: design.id },
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
        notifySuccess("Design deleted successfully.");
        await this.fetchDesigns();
      } catch (error) {
        console.error("Error deleting design:", error);
        notifyError("Could not delete the design. Please try again.");
      }
    },
    async editDesignName(design) {
      const newName = prompt("Enter a new name for your design:", design.name);

      // Check if the user entered a new name and didn't just click cancel or leave it empty
      if (newName && newName.trim() !== "" && newName.trim() !== design.name) {
        try {
          const response = await axios.put(
            `http://localhost:5000/api/designs/${design.id}`,
            { name: newName.trim() }, // Send the new name in the request body
            { withCredentials: true }
          );
          const index = this.designs.findIndex((d) => d.id === design.id);
          if (index !== -1) {
            this.designs[index].name = response.data.name;
          }
        } catch (error) {
          console.error("Error updating design name:", error);
          alert("Could not update the name. Please try again.");
        }
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
.design-title {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  border-radius: 5px;
  padding: 2px 6px;
  margin: -2px -6px;
  transition: background-color 0.2s;
}
.design-title:hover {
  background-color: #f0f2f5;
}
.design-title .edit-icon {
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 0.8em;
}
.design-title:hover .edit-icon {
  opacity: 0.7;
}
</style>
