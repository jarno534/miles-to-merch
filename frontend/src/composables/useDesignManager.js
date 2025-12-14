import { reactive, computed, ref } from "vue";

const getDefaultElementState = () => ({
  mapElement: {
    id: "map",
    visible: true,
    x: 0,
    y: 0,
    width: 300,
    height: 300,
    zIndex: 1,
  },
  mapSettings: {
    lineColor: "#ff0000",
    lineWeight: 3,
    gradientData: "none",
    style: "streets",
    visuals: "standard",
    fadeEdges: false,
    showStartEndMarkers: true,
    pitch: 45,
    bearing: 0,
  },
  dataFields: {
    id: "dataFields",
    visible: false,
    x: 50,
    y: -150,
    width: 300,
    height: 120,
    columns: 2,
    labelSize: 12,
    labelColor: "#666666",
    valueSize: 24,
    valueColor: "#333333",
    borderStyle: "inner",
    borderColor: "rgba(150, 150, 150, 0.8)",
    zIndex: 2,
    availableFields: [
      {
        id: "distance",
        label: "Distance",
        value: "-",
        selected: true,
        order: 1,
      },
      { id: "time", label: "Time", value: "-", selected: true, order: 2 },
      {
        id: "moving_time",
        label: "Moving Time",
        value: "-",
        selected: false,
        order: 3,
      },
      {
        id: "elapsed_time",
        label: "Elapsed Time",
        value: "-",
        selected: false,
        order: 4,
      },
      {
        id: "elevation_gain",
        label: "Elevation Gain",
        value: "-",
        selected: true,
        order: 5,
      },
      {
        id: "max_elevation",
        label: "Max Elevation",
        value: "-",
        selected: false,
        order: 6,
      },
      {
        id: "avg_pace",
        label: "Avg Pace",
        value: "-",
        selected: true,
        order: 7,
      },
      {
        id: "max_pace",
        label: "Max Pace",
        value: "-",
        selected: false,
        order: 8,
      },
      {
        id: "avg_speed",
        label: "Avg Speed",
        value: "-",
        selected: false,
        order: 9,
      },
      {
        id: "max_speed",
        label: "Max Speed",
        value: "-",
        selected: false,
        order: 10,
      },
      { id: "avg_hr", label: "Avg HR", value: "-", selected: false, order: 11 },
      { id: "max_hr", label: "Max HR", value: "-", selected: false, order: 12 },
      {
        id: "avg_cadence",
        label: "Avg Cadence",
        value: "-",
        selected: false,
        order: 13,
      },
      {
        id: "max_cadence",
        label: "Max Cadence",
        value: "-",
        selected: false,
        order: 14,
      },
      {
        id: "avg_power",
        label: "Avg Power",
        value: "-",
        selected: false,
        order: 15,
      },
      {
        id: "max_power",
        label: "Max Power",
        value: "-",
        selected: false,
        order: 16,
      },
    ],
  },
  weatherElement: {
    id: "weather",
    visible: false,
    x: 150,
    y: -200,
    width: 200,
    height: 80,
    zIndex: 10,
    fontSize: 18,
    textColor: "#333333",
    showIcon: true,
    backgroundColor: "#FFFFFF",
    transparentBg: true,
    borderRadius: 0,
  },
  badgeListElement: {
    id: "badgeList",
    visible: false,
    zIndex: 10,
    x: 0,
    y: 180,
    width: 350,
    height: 150,
    fontSize: 14,
    textColor: "#333333",
    backgroundColor: "#FFFFFF",
    transparentBg: true,
    fontFamily: "Arial",
    borderEnabled: false,
    borderColor: "#333333",
    borderWidth: 2,
  },
  graphElements: [],
  textBoxes: [],
  photoElements: [],
  qrCodeElements: [],
  achievements: [],
});

export function useDesignManager() {
  const currentView = ref("front"); // 'front', 'back', 'sleeve_left', etc.

  // State for each view.
  // Initialized with one 'front' view, others added dynamically or on init
  const designs = reactive({
    front: getDefaultElementState(),
  });

  const history = ref([]);
  const historyIndex = ref(-1);
  const isApplyingState = ref(false);
  const clipboard = ref(null);

  // Selection state needs to be global to the editor
  const selection = reactive({
    type: "map", // default to map
    item: null,
  });

  // --- Computed ---

  const currentDesign = computed(() => {
    if (!designs[currentView.value]) {
      // Lazy init if not exists
      designs[currentView.value] = getDefaultElementState();
    }
    return designs[currentView.value];
  });

  const canUndo = computed(() => historyIndex.value > 0);
  const canRedo = computed(() => historyIndex.value < history.value.length - 1);
  const canPaste = computed(() => !!clipboard.value);
  const canCopyCutDelete = computed(
    () => !!selection.type && selection.type !== "map"
  ); // Usually map is not deletable

  // --- Actions ---

  const switchView = (viewName) => {
    if (viewName !== currentView.value) {
      // Clear selection when switching views to avoid confusion
      deselectAll();
      currentView.value = viewName;
    }
  };

  const deselectAll = () => {
    selection.type = null;
    selection.item = null;
  };

  const selectElement = (type, item) => {
    selection.type = type;
    selection.item = item;
  };

  // Helper to clone state for history
  const cloneState = (state) => JSON.parse(JSON.stringify(state));

  const saveStateToHistory = () => {
    if (isApplyingState.value) return;

    // We save the WHOLE designs object to history?
    // Or just the current view? Design requirements say "multi-view support".
    // Usually undo/redo is global. Let's save the whole `designs` object.

    if (historyIndex.value < history.value.length - 1) {
      history.value.splice(historyIndex.value + 1);
    }
    history.value.push(cloneState(designs));
    historyIndex.value = history.value.length - 1;

    // Optional: Max history size
    if (history.value.length > 50) {
      history.value.shift();
      historyIndex.value--;
    }
  };

  const undo = () => {
    if (canUndo.value) {
      isApplyingState.value = true;
      historyIndex.value--;
      const state = history.value[historyIndex.value];
      Object.assign(designs, cloneState(state));
      isApplyingState.value = false;
    }
  };

  const redo = () => {
    if (canRedo.value) {
      isApplyingState.value = true;
      historyIndex.value++;
      const state = history.value[historyIndex.value];
      Object.assign(designs, cloneState(state));
      isApplyingState.value = false;
    }
  };

  // Generic add element
  const addElement = (type, payload) => {
    const design = currentDesign.value;
    switch (type) {
      case "textBox":
        design.textBoxes.push(payload);
        break;
      case "photo":
        design.photoElements.push(payload);
        break;
      case "graph":
        design.graphElements.push(payload);
        break;
      case "qrCode":
        design.qrCodeElements.push(payload);
        break;
    }
    selectElement(type, payload);
    saveStateToHistory();
  };

  const removeElement = (type, id) => {
    const design = currentDesign.value;
    switch (type) {
      case "textBox":
        design.textBoxes = design.textBoxes.filter((e) => e.id !== id);
        break;
      case "photo":
        design.photoElements = design.photoElements.filter((e) => e.id !== id);
        break;
      case "graph":
        design.graphElements = design.graphElements.filter((e) => e.id !== id);
        break;
      case "qrCode":
        design.qrCodeElements = design.qrCodeElements.filter(
          (e) => e.id !== id
        );
        break;
    }
    deselectAll();
    saveStateToHistory();
  };

  // Initialize history with initial state
  // Should be called after setup
  const initHistory = () => {
    history.value = [cloneState(designs)];
    historyIndex.value = 0;
  };

  return {
    currentView,
    designs,
    currentDesign,
    selection,
    clipboard, // Export clipboard
    canUndo,
    canRedo,
    canPaste,
    canCopyCutDelete,
    switchView,
    deselectAll,
    selectElement,
    addElement,
    removeElement,
    undo,
    redo,
    saveStateToHistory,
    initHistory,
    history,
  };
}
