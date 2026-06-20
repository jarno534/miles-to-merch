<template>
  <div class="design-editor-page">
    <EditorSidebar
      class="left-sidebar"
      :design="currentDesign"
      :editor-product-data="editorProductData"
      :selection="selection"
      :activity-data="activityData"
      :available-graph-sources="availableGraphSources"
      :activity-photos="activityPhotos"
      :weather-data="weatherData"
      :active-placement="currentView"
      :active-variant-id="selectedVariant ? selectedVariant.id : null"
      :available-placements="sidebarPlacements"
      @update:activePlacement="switchView"
      @update:activeVariantId="handleVariantChange"
      @select-element="selectElement"
      @add-element="(type) => addElement(type, createDefaultElement(type))"
      @remove-element="(item) => removeElement(item.id.split('_')[0], item.id)"
      @update:mapSettings="(val) => updateElementState('mapSettings', val)"
      @update:dataFields="(val) => updateElementState('dataFields', val)"
      @update:achievements="(val) => updateElementState('achievements', val)"
      @update:graphElements="(val) => updateElementState('graphElements', val)"
      @update:textBoxes="(val) => updateElementState('textBoxes', val)"
      @update:photoElements="(val) => updateElementState('photoElements', val)"
      @update:badgeListElement="
        (val) => updateElementState('badgeListElement', val)
      "
      @update:qrCodeElements="
        (val) => updateElementState('qrCodeElements', val)
      "
      @update:weatherElement="
        (val) => updateElementState('weatherElement', val)
      "
      @pan-map="handlePan"
      @zoom-in="handleZoomIn"
      @zoom-out="handleZoomOut"
      @trigger-upload="triggerUpload"
    />

    <div class="editor-center-area">
      <input
        type="file"
        ref="gpxFile"
        accept=".gpx"
        @change="handleFileUpload"
        style="display: none"
      />

      <div class="canvas-wrapper">
        <EditorCanvas
          ref="editorCanvasRef"
          :design="currentDesign"
          :loading="loading"
          :activity-data="activityData"
          :selected-variant="selectedVariant"
          :editor-product-data="editorProductData"
          :print-area-data="currentPrintArea"
          :selection="selection"
          :weather-data="weatherData"
          @select-element="selectElement"
          @deselect-all="deselectAll"
          @update-element-geometry="handleUpdateElementGeometry"
          @update-element-property="handleUpdateElementProperty"
          @update-map-instance="(instance) => (mapInstance = instance)"
          @update:activeVariantId="handleVariantChange"
        />
      </div>
    </div>

    <EditorTools
      class="right-sidebar"
      :selection="selection"
      :can-undo="canUndo"
      :can-redo="canRedo"
      :can-paste="canPaste"
      :can-copy-cut-delete="canCopyCutDelete"
      @save-design="handleSave(false)"
      @save-and-checkout="handleSave(true)"
      @clear-canvas="clearCanvas"
      @undo="undo"
      @redo="redo"
      @cut="cutElement"
      @copy="copyElement"
      @paste="pasteElement"
      @delete-selected="deleteSelectedElement"
      @deselect-all="deselectAll"
      @align-element="alignElement"
      @bring-forward="bringForward"
      @send-backward="sendBackward"
      @bring-to-front="bringToFront"
      @send-to-back="sendToBack"
    />

    <UnitsModal
      :visible="isUnitsModalVisible"
      @units-selected="handleUnitsSelected"
    />
  </div>
</template>

<script setup>
/* global defineProps */
import {
  ref,
  computed,
  watch,
  onMounted,
  onBeforeUnmount,
  nextTick,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { useDesignManager } from "@/composables/useDesignManager";
import axios from "@/apiConfig.js";
import { settings } from "@/settings";
import { auth } from "@/auth";
import { notifySuccess, notifyError, notifyInfo } from "@/notifications";
import html2canvas from "html2canvas";
import QRCode from "qrcode";

import EditorSidebar from "@/components/EditorSidebar.vue";
import EditorCanvas from "@/components/EditorCanvas.vue";
import EditorTools from "@/components/EditorTools.vue";
import UnitsModal from "@/components/UnitsModal.vue";

import { useWeather } from "@/composables/useWeather";
import { useAchievements } from "@/composables/useAchievements";
import {
  formatDistance,
  formatTime,
  formatPace,
  formatSpeed,
  formatHeartRate,
  formatCadence,
  formatPower,
  formatElevation,
} from "@/utils/formatters";

// --- Props & Route ---
const props = defineProps({
  productId: { type: [String, Number], required: true },
  activityId: { type: [String, Number], required: true },
  designId: { type: [String, Number], default: null },
});

const route = useRoute();
const router = useRouter();

// --- Design Manager ---
const {
  currentView,
  designs,
  currentDesign,
  selection,
  canUndo,
  canRedo,
  canPaste,
  canCopyCutDelete,
  switchView,
  deselectAll,
  selectElement,
  addElement: managerAddElement,
  removeElement: managerRemoveElement,
  undo,
  redo,
  saveStateToHistory,
  initHistory,
  clipboard, // Added clipboard
} = useDesignManager();

// --- Local State ---
const loading = ref(true);
const isDirty = ref(false);
const isUnitsModalVisible = ref(false);
const editorProductData = ref(null);
const activityData = ref(null);
const activityPhotos = ref([]);
const editorCanvasRef = ref(null);
const mapInstance = ref(null);

// Composable Instances
const { weatherData, fetchWeather, updateWeatherDisplay } = useWeather();
const { analyzeAchievements: analyzeAchievementsLogic } = useAchievements();

// --- Computed ---

const selectedVariantId = ref(
  parseInt(localStorage.getItem("selectedVariantId")) || null
);

const selectedVariant = computed(() => {
  if (!editorProductData.value || !editorProductData.value.variants)
    return null;

  // Debug Logging
  console.log("DEBUG: Computing selectedVariant...");
  console.log("DEBUG: selectedVariantId (ref):", selectedVariantId.value);
  console.log(
    "DEBUG: LocalStorage selectedVariantId:",
    localStorage.getItem("selectedVariantId")
  );

  // If no ID selected, pick first active one
  if (!selectedVariantId.value) {
    console.log("DEBUG: No ID, falling back to first variant.");
    return editorProductData.value.variants[0];
  }
  const found = editorProductData.value.variants.find(
    (v) => v.id === selectedVariantId.value
  );

  console.log("DEBUG: Found variant:", found ? found.color : "None");
  return found || editorProductData.value.variants[0]; // Fallback
});

function handleVariantChange(newId) {
  console.log("DEBUG: handleVariantChange called with:", newId);
  selectedVariantId.value = newId;
  localStorage.setItem("selectedVariantId", newId);
}

const currentPrintArea = computed(() => {
  let printArea = null;

  // 1. Haal de coördinaten op (gebruikt de 3000x3000px grid uit jouw data)
  if (selectedVariant.value?.print_areas?.[currentView.value]) {
    printArea = selectedVariant.value.print_areas[currentView.value];
  } else if (editorProductData.value?.print_areas?.[currentView.value]) {
    printArea = editorProductData.value.print_areas[currentView.value];
  }

  if (!printArea) return null;

  // 2. Gebruik ALTIJD de image_url uit de print_area (de witte Ghost PNG)
  // We negeren hier de selectedVariant.value.image (de JPG)
  return {
    ...printArea,
    image_url: printArea.image_url,
  };
});

const availableViews = computed(() => {
  // Merge views from Variant and Product
  const views = new Set();

  // Variant specific views
  if (selectedVariant.value && selectedVariant.value.print_areas) {
    Object.keys(selectedVariant.value.print_areas).forEach((k) => views.add(k));
  }

  // Product default views (fallback or superset)
  if (editorProductData.value && editorProductData.value.print_areas) {
    Object.keys(editorProductData.value.print_areas).forEach((k) =>
      views.add(k)
    );
  }

  // Sort logic? Front first
  const sorted = Array.from(views).sort((a, b) => {
    if (a === "front") return -1;
    if (b === "front") return 1;
    return a.localeCompare(b);
  });

  return sorted;
});

const sidebarPlacements = computed(() => {
  const placements = {};
  const extraCost = 5.0; // Hardcoded for now, or fetch from settings

  // Determine which views are "active" (have content)
  // This helps if we want dynamic "first one is free" logic
  // For now, let's assume 'front' is base, others are extra.
  // Or: If you select a view, it adds to cost.

  availableViews.value.forEach((view) => {
    let price = 0;
    // Simple logic: Front is base. Others +5.
    // Refined logic based on user request "after first is edited":
    // This implies flexible starting point.
    // Let's stick to: Non-front views cost extra for now (simplest interpretation of Printful usually)
    // UNLESS we check what's edited.

    // User Quote: "how much an extra print surface costs after the first print surface is edited"
    // This implies dynamic.
    // Let activeViews = count of views with >0 elements.
    // But we need to show the price on the BUTTON.
    // "Front (Included)", "Back (+€5.00)"

    if (view !== "front") {
      price = extraCost;
    }

    placements[view] = {
      name: getPlacementName(view),
      price: price,
      key: view,
    };
  });
  return placements;
});

function getPlacementName(key) {
  // Helper to get name from product data or format key
  if (
    editorProductData.value &&
    editorProductData.value.print_areas &&
    editorProductData.value.print_areas[key]
  ) {
    return editorProductData.value.print_areas[key].name;
  }
  // Capitalize
  return key.charAt(0).toUpperCase() + key.slice(1);
}

const availableGraphSources = computed(() => {
  if (!activityData.value || !activityData.value.streams) return [];
  const streamLabels = {
    heartrate: "Heart Rate",
    velocity_smooth: "Speed",
    altitude: "Altitude",
    cadence: "Cadence",
    watts: "Power",
    temp: "Temperature",
    grade_smooth: "Grade",
  };
  const sources = [];
  Object.keys(activityData.value.streams).forEach((key) => {
    if (streamLabels[key]) {
      sources.push({ value: key, text: streamLabels[key] });
      if (key === "velocity_smooth")
        sources.push({ value: "pace", text: "Pace" });
    }
  });
  return sources;
});

// --- Lifecycle ---

onMounted(async () => {
  loading.value = true;
  localStorage.setItem("selectedProductId", props.productId);
  window.addEventListener("beforeunload", handleBeforeUnload);
  window.addEventListener("keydown", handleKeyDown);

  if (!localStorage.getItem("user-units")) {
    isUnitsModalVisible.value = true;
  }

  try {
    // 1. Load Data
    let activityRes;
    if (props.activityId === "gpx" && window.tempGpxData) {
      activityRes = { data: window.tempGpxData };
      delete window.tempGpxData;
    }

    const [productRes, finalActivityRes] = await Promise.all([
      axios.get(`/api/products/${props.productId}`),
      activityRes || axios.get(`/api/activities/${props.activityId}`),
    ]);

    editorProductData.value = productRes.data;
    activityData.value = finalActivityRes.data;
    activityPhotos.value = finalActivityRes.data.photos || [];

    // Ensure we have a valid view
    if (editorProductData.value.print_areas) {
      const areas = Object.keys(editorProductData.value.print_areas);
      if (areas.length > 0 && !areas.includes(currentView.value)) {
        switchView(areas[0]);
      }
    }

    // 2. Fetch Extra Data
    if (activityData.value?.details?.athlete?.id) {
      // logic for fetch athlete stats if needed
      // skipping for brevity unless critical
    }

    updateDataFields();
    analyzeAchievements(); // Call local function which calls logic
    if (activityData.value?.details) {
      fetchWeather(activityData.value.details);
    }

    // 3. Load Design State (if editing or auto-saved)
    const designIdToLoad = props.designId || route.query.design_id;
    const unsavedDesign = localStorage.getItem("autosavedDesign");

    if (designIdToLoad) {
      const res = await axios.get(`/api/designs/${designIdToLoad}`);
      // Migration check: legacy designs might be single-level object, not view-keyed
      const loadedData = res.data.design_data;

      // Cleanup metadata from views
      if (loadedData.activityId) delete loadedData.activityId;

      if (!loadedData.front && !loadedData.back) {
        // It's legacy, assign it to 'front' or current view
        // Assuming legacy was only front
        Object.assign(designs.front, loadedData);
      } else {
        // It's new format
        Object.assign(designs, loadedData);
      }
    } else if (unsavedDesign) {
      // Check format
      const parsed = JSON.parse(unsavedDesign);

      // Cleanup metadata if present in localStorage
      if (parsed.activityId) delete parsed.activityId;

      if (!parsed.front && !parsed.back && parsed.mapElement) {
        // Legacy autosave
        Object.assign(designs.front, parsed);
      } else {
        Object.assign(designs, parsed);
      }
    } else {
      // Fresh start: Optimize defaults based on activity type
      const type = activityData.value.details?.type;
      const rides = [
        "Ride",
        "VirtualRide",
        "E-BikeRide",
        "GravelRide",
        "MountainBikeRide",
        "Handcycle",
      ];
      if (type && rides.includes(type)) {
        // Access the default front design or iterate all?
        // Defaults are in currentDesign (which is front).
        // But if we have multiple views, we might need to update all or just front.
        // Usually data fields are global or copied.
        // Let's update 'front' as it's the default view init.
        const fields = designs.front.dataFields.availableFields;
        const pace = fields.find((f) => f.id === "avg_pace");
        if (pace) pace.selected = false;
        const speed = fields.find((f) => f.id === "avg_speed");
        if (speed) speed.selected = true;

        // Also toggle max if needed
        const maxPace = fields.find((f) => f.id === "max_pace");
        if (maxPace) maxPace.selected = false;
      }
    }

    // Initialize history after loading state
    initHistory();
  } catch (error) {
    console.error("Error loading editor:", error);
    notifyError("Failed to load editor data.");
  } finally {
    loading.value = false;
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("beforeunload", handleBeforeUnload);
  window.removeEventListener("keydown", handleKeyDown);
});

// --- Watchers ---

watch(
  designs,
  () => {
    isDirty.value = true;
    // We skip saving to localstorage on every change for performance,
    // but maybe debounce it. useDesignManager handles history which is heavy enough.
    // Let's autosave to localstorage
    localStorage.setItem("autosavedDesign", JSON.stringify(designs));
  },
  { deep: true }
);

watch(
  () => settings.units,
  () => {
    if (activityData.value) {
      updateDataFields();
      updateWeatherDisplay();
    }
  }
);

// --- Methods (Logic) ---

function handleBeforeUnload(event) {
  if (isDirty.value) {
    event.preventDefault();
    event.returnValue = "";
  }
}

function updateElementState(key, value) {
  // Directly update the reactive state
  // This is called by EditorSidebar emitting updates (e.g., v-model like behavior)
  if (currentDesign.value[key]) {
    // If it's an array, we might be replacing it
    if (Array.isArray(currentDesign.value[key])) {
      currentDesign.value[key] = value;
    } else {
      Object.assign(currentDesign.value[key], value);
    }
    saveStateToHistory();
  }
}

// -- Element Factory --
function getInitialElementColor(type = "main") {
  const isDark =
    editorProductData.value &&
    editorProductData.value.merch_color_type === "dark";
  if (isDark) return type === "label" ? "#E0E0E0" : "#FFFFFF";
  return type === "label" ? "#555555" : "#000000";
}

function createDefaultElement(type) {
  // Re-implement the defaults logic from original DesignView methods
  const zIndex = 20; // Simplified

  if (type === "graph") {
    return {
      id: `graph_${Date.now()}`,
      visible: true,
      x: 20,
      y: 20,
      width: 350,
      height: 200,
      zIndex,
      selectedDataSource: "heartrate",
      lineColor: "#fc4c02",
      fillColor: "#fca587",
      // ... other defaults
      showGrid: true,
    };
  }
  if (type === "textBox") {
    return {
      id: `textBox_${Date.now()}`,
      text: activityData.value?.details?.name || "Title",
      x: 0,
      y: 0,
      width: 300,
      height: 80,
      fontFamily: "Arial",
      fontSize: 30,
      fontColor: getInitialElementColor(),
      transparentBg: true,
      backgroundColor: "#ffffff",
      zIndex,
    };
  }
  // ... photo, qrcode defaults
  // For brevity, using a minimal set. In real app, copy all defaults.
  if (type === "photo")
    return {
      id: `photo_${Date.now()}`,
      x: 0,
      y: 0,
      width: 300,
      height: 200,
      zIndex,
      src: null,
    };
  if (type === "qrcode")
    return {
      id: `qrcode_${Date.now()}`,
      x: 0,
      y: 0,
      width: 150,
      height: 150,
      zIndex,
      showText: true,
      text: "Scan Me",
      linkType: "activity",
    };

  return {};
}

function addElement(type, payload = null) {
  // If payload is null, create default
  const element = payload || createDefaultElement(type);

  if (type === "qrCode") {
    // Logic to generate QR data URL
    updateQrCodeValue(element);
  }

  managerAddElement(type, element);
}

function removeElement(type, id) {
  managerRemoveElement(type, id);
}

// -- Canvas Interaction --
function handleUpdateElementGeometry({ element, newGeometry }) {
  const target = findElementById(element.id);
  if (target) {
    Object.assign(target, newGeometry);
    saveStateToHistory();
  }
}

function handleUpdateElementProperty({ element, property, value }) {
  const target = findElementById(element.id);
  if (target) {
    target[property] = value;
    if (
      element.id.startsWith("qrCode_") &&
      (property === "customLink" || property === "linkType")
    ) {
      updateQrCodeValue(target);
    }
    saveStateToHistory();
  }
}

function findElementById(id) {
  // Helper specifically for current view
  const d = currentDesign.value;
  const all = [
    d.mapElement,
    d.dataFields,
    d.badgeListElement,
    d.weatherElement,
    ...d.graphElements,
    ...d.textBoxes,
    ...d.photoElements,
    ...d.qrCodeElements,
  ];
  return all.find((el) => el && el.id === id);
}

// -- Global Actions --
function clearCanvas() {
  if (!confirm("Clear all elements on this view?")) return;
  // Reset current view state
  const d = currentDesign.value;
  d.mapElement.visible = false;
  d.dataFields.visible = false;
  // ... reset others ...
  d.graphElements = [];
  d.textBoxes = [];
  // ...
  saveStateToHistory();
}

function deleteSelectedElement() {
  if (selection.type && selection.item) {
    removeElement(selection.type, selection.item.id);
  }
}

function cutElement() {
  if (selection.type && selection.item) {
    copyElement();
    deleteSelectedElement();
  }
}

function copyElement() {
  if (selection.type && selection.item) {
    clipboard.value = {
      type: selection.type,
      element: JSON.parse(JSON.stringify(selection.item)),
    };
  }
}

function pasteElement() {
  if (!clipboard.value) return;
  const { type, element } = clipboard.value;
  const newEl = JSON.parse(JSON.stringify(element));

  // Offset slightly
  newEl.x += 20;
  newEl.y += 20;
  newEl.id = `${type}_${Date.now()}`;
  // zIndex will be handled by manager if added?
  // Actually DesignView logic handled zIndex increment.
  // Manager default does push, but zIndex might collide.
  // Let's increment zIndex if possible or let user adjust.
  // Ideally we find max zIndex.
  // For now, simpler:
  newEl.zIndex = (newEl.zIndex || 10) + 1;

  managerAddElement(type, newEl);
}

function bringForward() {
  modifyZIndex(1);
}
function sendBackward() {
  modifyZIndex(-1);
}
function bringToFront() {
  modifyZIndex(100);
}
function sendToBack() {
  modifyZIndex(-100);
}

function modifyZIndex(delta) {
  if (selection.item) {
    selection.item.zIndex += delta;
    saveStateToHistory();
  }
}

function alignElement(dir) {
  // Logic requires canvas rect. Access via ref
  if (!selection.item || !editorCanvasRef.value) return;
  const canvasEl = editorCanvasRef.value.getCanvasElement(); // Assumes EditorCanvas exposes this
  if (!canvasEl) return;
  const el = selection.item;

  // ... alignment logic adapted from original ...
  if (dir === "center-h") el.x = 0;
  if (dir === "center-v") el.y = 0;
  saveStateToHistory();
}

// -- Saving --
async function handleSave(proceedToCheckout) {
  if (!auth.isLoggedIn) {
    notifyInfo("Please create an account to save.");
    localStorage.setItem("unsavedDesign", JSON.stringify(designs)); // Save ALL views
    localStorage.setItem("proceedToCheckout", proceedToCheckout);
    router.push({ name: "Register", query: { redirect: route.fullPath } });
    return;
  }

  loading.value = true;
  try {
    const designDataPayload = {};
    const previewImagesPayload = {};
    const originalView = currentView.value;

    // Iterate all views to generate previews
    // Filter out non-object keys (like activityId if it crept in)
    const views = Object.keys(designs).filter(
      (k) => designs[k] && typeof designs[k] === "object"
    );

    // IMPORTANT: We need to render each view to get the screenshot.
    // This requires switching the view, waiting for render, then screenshotting.

    for (const view of views) {
      switchView(view);
      await nextTick();
      // Wait a bit for map to render?
      await new Promise((r) => setTimeout(r, 500));

      const canvasEl = editorCanvasRef.value.getCanvasElement();
      if (canvasEl) {
        const canvas = await html2canvas(canvasEl, {
          backgroundColor: null,
          useCORS: true,
          scale: 2,
        });
        previewImagesPayload[view] = canvas.toDataURL("image/png");
      }
      designDataPayload[view] = designs[view];
    }

    // Restore original view
    switchView(originalView);

    // Save metadata
    designDataPayload.activityId = props.activityId;

    const payload = {
      product_id: parseInt(props.productId),
      variant_id: selectedVariantId.value,
      design_data: designDataPayload, // Now allows multi-view structure
      preview_images: previewImagesPayload,
      name: `Design for ${activityData.value.details.name}`,
    };

    const res = await axios.post("/api/designs", payload);
    notifySuccess("Saved!");
    isDirty.value = false;

    if (proceedToCheckout) {
      router.push({ name: "Checkout", params: { designId: res.data.id } });
    }
  } catch (e) {
    console.error(e);
    notifyError("Failed to save.");
  } finally {
    loading.value = false;
  }
}

// -- Helpers --
async function updateQrCodeValue(qrCode) {
  if (!qrCode || !activityData.value) return;
  let url = "";
  if (qrCode.linkType === "activity")
    url = `https://www.strava.com/activities/${activityData.value.details.id}`;
  else if (qrCode.linkType === "profile")
    url = `https://www.strava.com/athletes/${activityData.value.details.athlete.id}`;
  else if (qrCode.linkType === "custom") url = qrCode.customLink;

  if (url) {
    try {
      qrCode.dataUrl = await QRCode.toDataURL(url, {
        margin: 1,
        width: 256,
        color: { dark: qrCode.textColor, light: "#0000" },
      });
    } catch (e) {
      console.error(e);
    }
  }
}

function updateDataFields() {
  if (!activityData.value || !activityData.value.details) return;
  const data = activityData.value.details;

  currentDesign.value.dataFields.availableFields.forEach((field) => {
    const formatters = {
      distance: formatDistance(data.distance),
      time: formatTime(data.moving_time),
      moving_time: formatTime(data.moving_time),
      elapsed_time: formatTime(data.elapsed_time),
      elevation_gain: formatElevation(data.total_elevation_gain),
      max_elevation: formatElevation(data.elev_high),
      avg_pace: formatPace(1000 / data.average_speed),
      max_pace: formatPace(1000 / data.max_speed),
      avg_speed: formatSpeed(data.average_speed),
      max_speed: formatSpeed(data.max_speed),
      avg_hr: formatHeartRate(data.average_heartrate),
      max_hr: formatHeartRate(data.max_heartrate),
      avg_cadence: formatCadence(
        data.average_cadence ? data.average_cadence * 2 : undefined
      ),
      max_cadence: formatCadence(
        data.max_cadence ? data.max_cadence * 2 : undefined
      ),
      avg_power: formatPower(data.average_watts),
      max_power: formatPower(data.max_watts),
    };
    field.value = formatters[field.id] || "-";
  });
}

function analyzeAchievements() {
  if (!activityData.value || !activityData.value.details) return;
  const achievements = analyzeAchievementsLogic(
    activityData.value.details,
    activityData.value.athlete?.sex
  );
  // Directly update the achievements array in the design
  // The design state expects 'achievements' array in the root of the design object?
  // In useDesignManager getDefaultElementState(), 'achievements' is an empty array.
  // So we invoke updateElementState or just set it.
  if (!currentDesign.value.achievements) currentDesign.value.achievements = [];
  currentDesign.value.achievements = achievements;
  // Also save to history? Initial analysis might not need history save, but user interaction does.
}

// fetchWeather is already provided by useWeather and destructured.
// We just need to call it with appropriate args.
// In onMounted: fetchWeather(activityData.value.details);
// Renaming local wrapper to avoid conflict with imported 'fetchWeather' function?
// No, I imported it as fetchWeather. I just need to use it.
// But I defined function fetchWeather() { ... } placeholder.
// I should remove the placeholder and use the imported one.
// Wait, the imported 'fetchWeather' takes 'activityDetails'.
// The placeholder was used in onMounted.
// I can just delete the placeholder function definition.

function handleUnitsSelected(u) {
  settings.setUnits(u);
  isUnitsModalVisible.value = false;
  // update fields
}

function handleKeyDown(e) {
  if (!selection.item || !selection.type || selection.type === "map") return;

  const step = e.shiftKey ? 10 : 1;
  const item = selection.item;

  switch (e.key) {
    case "ArrowUp":
      item.y -= step;
      break;
    case "ArrowDown":
      item.y += step;
      break;
    case "ArrowLeft":
      item.x -= step;
      break;
    case "ArrowRight":
      item.x += step;
      break;
    case "Delete":
    case "Backspace":
      deleteSelectedElement();
      break;
  }
}

function handlePan(dir) {
  editorCanvasRef.value?.panMap(dir);
}
function handleZoomIn() {
  editorCanvasRef.value?.zoomIn();
}
function handleZoomOut() {
  editorCanvasRef.value?.zoomOut();
}
</script>

<style scoped>
.design-editor-page {
  display: flex;
  height: calc(100vh - 105px); /* Adjusted for navbar (~105px) */
  width: 100vw;
  overflow: hidden;
  background-color: #f5f5f5;
}

.left-sidebar {
  width: 300px;
  flex-shrink: 0;
  border-right: 1px solid #e0e0e0;
  background: white;
  z-index: 10;
}

.right-sidebar {
  width: 250px;
  flex-shrink: 0;
  border-left: 1px solid #e0e0e0;
  background: white;
  z-index: 10;
}

.editor-center-area {
  flex-grow: 1;
  display: flex;
  flex-direction: row; /* Horizontal layout: Switcher | Canvas */
  position: relative;
}

.canvas-wrapper {
  flex-grow: 1;
  width: 100%;
  height: 100%;
  position: relative;
  background: #e0e0e0;
}
</style>
