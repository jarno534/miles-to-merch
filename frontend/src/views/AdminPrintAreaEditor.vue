<template>
  <div class="admin-canvas-editor">
    <div class="header">
      <h2>Edit Print Area Canvas</h2>
      <button class="btn btn-secondary" @click="goBack">
        Back to Products
      </button>
    </div>

    <div v-if="loading" class="loading">Loading product data...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="editor-layout">
      <!-- Left Sidebar: Settings -->
      <div class="settings-panel">
        <h3>{{ product.name }}</h3>

        <div class="form-group">
          <label>Select Placement:</label>
          <select
            v-model="selectedPlacement"
            @change="onPlacementChange"
            class="form-control"
          >
            <option
              v-for="(area, key) in availablePlacements"
              :key="key"
              :value="key"
            >
              {{ key }}
            </option>
          </select>
        </div>

        <div v-if="currentConfig" class="config-form">
          <div class="form-group">
            <label>Background Image URL:</label>
            <input
              type="text"
              v-model="currentConfig.image_url"
              class="form-control"
              @input="updateBgImage"
            />
            <small>If empty, uses Variant 0 image.</small>
          </div>

          <div class="form-group toggle-group">
            <label>
              <input type="checkbox" v-model="currentConfig.is_ghost" />
              Is Ghost Template? (Enable CSS tinting)
            </label>
          </div>

          <h4>Canvas Dimensions (Auto-calculated from image)</h4>
          <p>Width: {{ currentConfig.mockup_width }}px</p>
          <p>Height: {{ currentConfig.mockup_height }}px</p>

          <h4>Print Area (Drag to change)</h4>
          <p>Left: {{ Math.round(currentConfig.left) }}</p>
          <p>Top: {{ Math.round(currentConfig.top) }}</p>
          <p>Width: {{ Math.round(currentConfig.width) }}</p>
          <p>Height: {{ Math.round(currentConfig.height) }}</p>

          <button
            class="btn btn-primary mt-4"
            @click="saveConfiguration"
            :disabled="saving"
          >
            {{ saving ? "Saving..." : "Save All Configurations" }}
          </button>

          <button class="btn btn-danger mt-2" @click="resetToPrintful">
            Reset this placement to Printful Defaults
          </button>
        </div>
      </div>

      <!-- Right Side: Canvas Preview -->
      <div class="canvas-panel">
        <div class="canvas-wrapper" ref="canvasWrapper">
          <img
            ref="bgImage"
            :src="previewImageUrl"
            @load="onImageLoad"
            class="background-preview"
            crossorigin="anonymous"
          />
          <div
            v-if="currentConfig && dimensionsLoaded"
            class="draggable-box"
            :style="boxStyle"
            @mousedown.prevent="startDrag"
          >
            <div
              class="resize-handle top-left"
              @mousedown.stop.prevent="startResize($event, 'top-left')"
            ></div>
            <div
              class="resize-handle top-right"
              @mousedown.stop.prevent="startResize($event, 'top-right')"
            ></div>
            <div
              class="resize-handle bottom-left"
              @mousedown.stop.prevent="startResize($event, 'bottom-left')"
            ></div>
            <div
              class="resize-handle bottom-right"
              @mousedown.stop.prevent="startResize($event, 'bottom-right')"
            ></div>
            <span class="box-label">Print Area</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

export default {
  name: "AdminPrintAreaEditor",
  setup() {
    const route = useRoute();
    const router = useRouter();

    const loading = ref(true);
    const saving = ref(false);
    const error = ref(null);
    const product = ref(null);

    const manualConfig = ref({});
    const availablePlacements = ref({});
    const selectedPlacement = ref(null);

    const bgImage = ref(null);
    const canvasWrapper = ref(null);
    const dimensionsLoaded = ref(false);

    // Drag state
    const isDragging = ref(false);
    const isResizing = ref(false);
    const resizeHandle = ref(null);
    const startX = ref(0);
    const startY = ref(0);
    const startBox = ref({ left: 0, top: 0, width: 0, height: 0 });

    const fetchProduct = async () => {
      try {
        const response = await api.get("/admin/products");
        const productId = parseInt(route.params.id);
        const p = response.data.find((prod) => prod.id === productId);

        if (!p) throw new Error("Product not found");

        product.value = p;
        availablePlacements.value = p.print_areas || {};

        // Clone existing manual config or start empty
        manualConfig.value = JSON.parse(
          JSON.stringify(p.manual_print_areas || {})
        );

        // Auto-select first placement
        const placements = Object.keys(availablePlacements.value);
        if (placements.length > 0) {
          selectedPlacement.value = placements[0];
          onPlacementChange();
        }
      } catch (err) {
        error.value = err.message || "Failed to load product";
      } finally {
        loading.value = false;
      }
    };

    const currentConfig = computed(() => {
      if (!selectedPlacement.value) return null;
      return manualConfig.value[selectedPlacement.value];
    });

    const previewImageUrl = computed(() => {
      if (currentConfig.value?.image_url) return currentConfig.value.image_url;
      // Fallback to variant image
      if (product.value?.variants?.length > 0) {
        return product.value.variants[0].image;
      }
      return null;
    });

    const onPlacementChange = () => {
      dimensionsLoaded.value = false;
      const placement = selectedPlacement.value;
      if (!placement) return;

      // If we don't have a config for this placement yet, initialize it with Printful defaults
      if (!manualConfig.value[placement]) {
        const printfulData = availablePlacements.value[placement] || {};
        manualConfig.value[placement] = {
          left: printfulData.left || 0,
          top: printfulData.top || 0,
          width: printfulData.width || 500,
          height: printfulData.height || 500,
          mockup_width: printfulData.mockup_width || 1000,
          mockup_height: printfulData.mockup_height || 1000,
          image_url: printfulData.image_url || "",
          is_ghost: false, // default false for manual overrides usually
        };
      }
    };

    const resetToPrintful = () => {
      if (confirm("Reset to Printful default coordinates?")) {
        delete manualConfig.value[selectedPlacement.value];
        onPlacementChange();
      }
    };

    const onImageLoad = () => {
      const img = bgImage.value;
      if (img && currentConfig.value) {
        currentConfig.value.mockup_width = img.naturalWidth;
        currentConfig.value.mockup_height = img.naturalHeight;
        dimensionsLoaded.value = true;
      }
    };

    const updateBgImage = () => {
      dimensionsLoaded.value = false;
    };

    // Style for the draggable box based on intrinsic dimensions
    const boxStyle = computed(() => {
      if (!currentConfig.value || !dimensionsLoaded.value) return {};
      const mw = currentConfig.value.mockup_width;
      const mh = currentConfig.value.mockup_height;
      if (!mw || !mh) return {};

      return {
        left: `${(currentConfig.value.left / mw) * 100}%`,
        top: `${(currentConfig.value.top / mh) * 100}%`,
        width: `${(currentConfig.value.width / mw) * 100}%`,
        height: `${(currentConfig.value.height / mh) * 100}%`,
      };
    });

    // Mouse events for dragging and resizing
    // We convert pixels back and forth to intrinsic image coordinates
    const getIntrinsicCoords = (e) => {
      const rect = bgImage.value.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const mw = currentConfig.value.mockup_width;
      const mh = currentConfig.value.mockup_height;

      // Ratio of actual display size to intrinsic size
      const scaleX = mw / rect.width;
      const scaleY = mh / rect.height;

      return {
        x: x * scaleX,
        y: y * scaleY,
      };
    };

    const startDrag = (e) => {
      if (isResizing.value) return;
      isDragging.value = true;
      const coords = getIntrinsicCoords(e);
      startX.value = coords.x;
      startY.value = coords.y;

      startBox.value = {
        left: currentConfig.value.left,
        top: currentConfig.value.top,
      };

      document.addEventListener("mousemove", onDrag);
      document.addEventListener("mouseup", stopInteraction);
    };

    const onDrag = (e) => {
      if (!isDragging.value) return;
      const coords = getIntrinsicCoords(e);
      const dx = coords.x - startX.value;
      const dy = coords.y - startY.value;

      currentConfig.value.left = startBox.value.left + dx;
      currentConfig.value.top = startBox.value.top + dy;
    };

    const startResize = (e, handle) => {
      isResizing.value = true;
      resizeHandle.value = handle;
      const coords = getIntrinsicCoords(e);
      startX.value = coords.x;
      startY.value = coords.y;

      startBox.value = {
        left: currentConfig.value.left,
        top: currentConfig.value.top,
        width: currentConfig.value.width,
        height: currentConfig.value.height,
      };

      document.addEventListener("mousemove", onResize);
      document.addEventListener("mouseup", stopInteraction);
    };

    const onResize = (e) => {
      if (!isResizing.value) return;
      const coords = getIntrinsicCoords(e);
      const dx = coords.x - startX.value;
      const dy = coords.y - startY.value;

      if (resizeHandle.value.includes("right")) {
        currentConfig.value.width = Math.max(10, startBox.value.width + dx);
      }
      if (resizeHandle.value.includes("bottom")) {
        currentConfig.value.height = Math.max(10, startBox.value.height + dy);
      }
      if (resizeHandle.value.includes("left")) {
        const newWidth = Math.max(10, startBox.value.width - dx);
        const shiftX = startBox.value.width - newWidth;
        currentConfig.value.left = startBox.value.left + shiftX;
        currentConfig.value.width = newWidth;
      }
      if (resizeHandle.value.includes("top")) {
        const newHeight = Math.max(10, startBox.value.height - dy);
        const shiftY = startBox.value.height - newHeight;
        currentConfig.value.top = startBox.value.top + shiftY;
        currentConfig.value.height = newHeight;
      }
    };

    const stopInteraction = () => {
      isDragging.value = false;
      isResizing.value = false;
      resizeHandle.value = null;
      document.removeEventListener("mousemove", onDrag);
      document.removeEventListener("mousemove", onResize);
      document.removeEventListener("mouseup", stopInteraction);
    };

    const saveConfiguration = async () => {
      saving.value = true;
      try {
        await api.post(
          `/admin/products/${product.value.id}/manual_print_areas`,
          {
            manual_print_areas: manualConfig.value,
          }
        );
        alert("Saved successfully!");
      } catch (err) {
        alert("Failed to save: " + (err.response?.data?.error || err.message));
      } finally {
        saving.value = false;
      }
    };

    const goBack = () => router.push("/admin");

    onMounted(() => {
      fetchProduct();
    });

    return {
      loading,
      saving,
      error,
      product,
      availablePlacements,
      selectedPlacement,
      currentConfig,
      previewImageUrl,
      onPlacementChange,
      resetToPrintful,
      updateBgImage,
      bgImage,
      canvasWrapper,
      dimensionsLoaded,
      onImageLoad,
      boxStyle,
      startDrag,
      startResize,
      saveConfiguration,
      goBack,
    };
  },
};
</script>

<style scoped>
.admin-canvas-editor {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.editor-layout {
  display: flex;
  gap: 20px;
  height: calc(100vh - 150px);
}

.settings-panel {
  width: 350px;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  overflow-y: auto;
}

.canvas-panel {
  flex-grow: 1;
  background: #e9ecef;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  padding: 20px;
}

.canvas-wrapper {
  position: relative;
  max-width: 100%;
  max-height: 100%;
  display: inline-block;
}

.background-preview {
  max-width: 100%;
  max-height: calc(100vh - 200px);
  display: block;
  object-fit: contain;
}

.draggable-box {
  position: absolute;
  border: 2px dashed #007bff;
  background: rgba(0, 123, 255, 0.2);
  cursor: move;
}

.box-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-weight: bold;
  text-shadow: 1px 1px 2px #000;
  pointer-events: none;
}

.resize-handle {
  position: absolute;
  width: 12px;
  height: 12px;
  background: #fff;
  border: 2px solid #007bff;
  border-radius: 50%;
}

.top-left {
  top: -6px;
  left: -6px;
  cursor: nwse-resize;
}
.top-right {
  top: -6px;
  right: -6px;
  cursor: nesw-resize;
}
.bottom-left {
  bottom: -6px;
  left: -6px;
  cursor: nesw-resize;
}
.bottom-right {
  bottom: -6px;
  right: -6px;
  cursor: nwse-resize;
}

.form-group {
  margin-bottom: 15px;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.mt-4 {
  margin-top: 1.5rem;
}
.mt-2 {
  margin-top: 0.5rem;
}
</style>
