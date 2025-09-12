<template>
  <div class="design-editor-page">
    <EditorSidebar
      :selection="selection"
      :activity-data="activityData"
      :available-graph-sources="availableGraphSources"
      :activity-photos="activityPhotos"
      :weather-data="weatherData"
      :editor-product-data="editorProductData"
      v-model:active-placement="activePlacement"
      v-model:achievements="achievements"
      v-model:mapSettings="mapSettings"
      v-model:dataFields="dataFields"
      v-model:graphElements="graphElements"
      v-model:textBoxes="textBoxes"
      v-model:photoElements="photoElements"
      v-model:badgeListElement="badgeListElement"
      v-model:qrCodeElements="qrCodeElements"
      v-model:weatherElement="weatherElement"
      @select-element="selectElement"
      @add-element="addElement"
      @remove-element="removeElement"
      @pan-map="handlePan"
      @zoom-in="handleZoomIn"
      @zoom-out="handleZoomOut"
      @update:selection-item-property="handleSelectionPropertyUpdate"
    />

    <div class="editor-main-area">
      <EditorCanvas
        ref="editorCanvas"
        :loading="loading"
        :activity-data="activityData"
        :editor-product-data="editorProductData"
        :print-area-data="currentPrintArea"
        :selection="selection"
        :map-element="mapElement"
        :map-settings="mapSettings"
        :data-fields="dataFields"
        :graph-elements="graphElements"
        :text-boxes="textBoxes"
        :photo-elements="photoElements"
        :badge-list-element="badgeListElement"
        :achievements="achievements"
        :qr-code-elements="qrCodeElements"
        :weather-element="weatherElement"
        :weather-data="weatherData"
        @select-element="selectElement"
        @deselect-all="deselectAll"
        @update-element-geometry="updateElementGeometry"
        @update-map-instance="map = $event"
        @update-element-property="handleElementPropertyUpdate"
      />
    </div>

    <EditorTools
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

<script>
import axios from "@/apiConfig.js";
import EditorSidebar from "@/components/EditorSidebar.vue";
import EditorCanvas from "@/components/EditorCanvas.vue";
import EditorTools from "@/components/EditorTools.vue";
import QRCode from "qrcode";
import { auth } from "../auth";
import { settings } from "../settings";
import html2canvas from "html2canvas";
import { notifySuccess, notifyError, notifyInfo } from "../notifications";
import UnitsModal from "@/components/UnitsModal.vue";

export default {
  name: "DesignView",
  props: {
    productId: {
      type: [String, Number],
      required: true,
    },
    activityId: {
      type: [String, Number],
      required: true,
    },
    designId: {
      type: [String, Number],
      required: false,
      default: null,
    },
  },
  components: {
    EditorSidebar,
    EditorCanvas,
    EditorTools,
    UnitsModal,
  },
  data() {
    return {
      currentPrintArea: null,
      activePlacement: "front",
      editorProductData: null,
      isDirty: false,
      settings: settings,
      isUnitsModalVisible: false,
      athleteStats: null,
      rawWeatherTemp: null,
      weatherData: null,
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
      achievements: [],
      badgeListElement: {
        id: "badgeList",
        visible: false,
        x: 0,
        y: 180,
        width: 350,
        height: 150,
        zIndex: 10,
        fontSize: 14,
        textColor: "#333333",
        backgroundColor: "#FFFFFF",
        transparentBg: true,
        fontFamily: "Arial",
        borderEnabled: false,
        borderColor: "#333333",
        borderWidth: 2,
      },
      zIndexCounter: 11,
      clipboard: null,
      history: [],
      historyIndex: -1,
      isApplyingState: false,
      activityData: null,
      activityPhotos: [],
      loading: true,
      map: null,
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
          {
            id: "avg_hr",
            label: "Avg HR",
            value: "-",
            selected: false,
            order: 11,
          },
          {
            id: "max_hr",
            label: "Max HR",
            value: "-",
            selected: false,
            order: 12,
          },
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
      graphElements: [],
      textBoxes: [],
      photoElements: [],
      qrCodeElements: [],
      selection: {
        type: "map",
        item: null,
      },
      elementKeyMap: {
        map: "mapElement",
        dataFields: "dataFields",
        badgeList: "badgeListElement",
        weather: "weatherElement",
      },
    };
  },

  computed: {
    availableGraphSources() {
      if (!this.activityData || !this.activityData.streams) {
        return [];
      }
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
      Object.keys(this.activityData.streams).forEach((key) => {
        if (streamLabels[key]) {
          sources.push({
            value: key,
            text: streamLabels[key],
          });

          if (key === "velocity_smooth") {
            sources.push({
              value: "pace",
              text: "Pace",
            });
          }
        }
      });
      return sources;
    },
    canUndo() {
      return this.historyIndex > 0;
    },
    canRedo() {
      return this.historyIndex < this.history.length - 1;
    },
    canCopyCutDelete() {
      return !!this.selection.type;
    },
    activeElementObject() {
      if (!this.selection.type) return null;
      if (this.selection.item) return this.selection.item;
      const key = this.elementKeyMap[this.selection.type];
      return this[key] || null;
    },
    canPaste() {
      return !!this.clipboard;
    },
    designState() {
      return {
        productId: this.productId,
        activityId: this.activityId,
        mapSettings: JSON.parse(JSON.stringify(this.mapSettings)),
        mapElement: JSON.parse(JSON.stringify(this.mapElement)),
        dataFields: JSON.parse(JSON.stringify(this.dataFields)),
        graphElements: JSON.parse(JSON.stringify(this.graphElements)),
        textBoxes: JSON.parse(JSON.stringify(this.textBoxes)),
        photoElements: JSON.parse(JSON.stringify(this.photoElements)),
        badgeListElement: JSON.parse(JSON.stringify(this.badgeListElement)),
        qrCodeElements: JSON.parse(JSON.stringify(this.qrCodeElements)),
        weatherElement: JSON.parse(JSON.stringify(this.weatherElement)),
      };
    },
  },
  watch: {
    activePlacement() {
      this.updatePrintArea();
    },

    editorProductData(newData) {
    if (newData && newData.print_areas) {
      const availablePlacements = Object.keys(newData.print_areas);
      if (availablePlacements.length > 0 && !availablePlacements.includes(this.activePlacement)) {
        this.activePlacement = availablePlacements[0];
      }
    }
    this.updatePrintArea();
  },

    designState: {
      handler() {
        if (this.isApplyingState) return;
        this.isDirty = true;
        if (this.historyIndex < this.history.length - 1) {
          this.history.splice(this.historyIndex + 1);
        }
        this.history.push(this.designState);
        this.historyIndex = this.history.length - 1;
        localStorage.setItem(
          "autosavedDesign",
          JSON.stringify(this.designState)
        );
      },
      deep: true,
    },

    activityData(newData) {
      if (newData) {
        this.updateDataFields();
        this.fetchWeather();
      }
    },

    "selection.item": {
      handler(newItem, oldItem) {
        if (this.selection.type !== "qrCode" || !newItem) return;

        if (!oldItem) return;

        if (newItem.linkType !== oldItem.linkType) {
          switch (newItem.linkType) {
            case "activity":
              newItem.text = "Give me Kudos!";
              break;
            case "profile":
              newItem.text = "Follow me!";
              break;
            case "custom":
              newItem.text = "Scan Me!";
              break;
          }
        }

        const hasRelevantChange =
          newItem.linkType !== oldItem.linkType ||
          newItem.transparentElementBg !== oldItem.transparentElementBg ||
          newItem.textColor !== oldItem.textColor ||
          (newItem.linkType === "custom" &&
            newItem.customLink !== oldItem.customLink);

        if (hasRelevantChange) {
          this.updateQrCodeValue(newItem);
        }
      },
      deep: true,
    },

    qrCodeElements: {
      handler(newQrCodes) {
        if (this.selection.type === "qrCode" && this.selection.item) {
          const updatedItem = newQrCodes.find(
            (q) => q.id === this.selection.item.id
          );
          if (updatedItem && this.selection.item !== updatedItem) {
            this.selection.item = updatedItem;
          }
        }
      },
      deep: true,
    },
  },

  methods: {
    updatePrintArea() {
      if (!this.editorProductData || !this.editorProductData.print_areas || !this.activePlacement) {
        this.currentPrintArea = null;
        return;
      }
      
      const printArea = this.editorProductData.print_areas[this.activePlacement];
      const selectedVariantId = parseInt(localStorage.getItem("selectedVariantId"));
      
      if (!selectedVariantId || !this.editorProductData.variants) {
        this.currentPrintArea = printArea;
        return;
      }

      const selectedVariant = this.editorProductData.variants.find(v => v.id === selectedVariantId);

      if (printArea && selectedVariant && selectedVariant.image_base_path) {
        this.currentPrintArea = {
          ...printArea,
          image_url: `/${selectedVariant.image_base_path}/${this.activePlacement}.jpg`
        };
      } else {
        this.currentPrintArea = printArea;
      }
    },

    getInitialElementColor(type = "main") {
      const isDark =
        this.editorProductData &&
        this.editorProductData.merch_color_type === "dark";
      if (isDark) {
        return type === "label" ? "#E0E0E0" : "#FFFFFF";
      } else {
        return type === "label" ? "#555555" : "#000000";
      }
    },

    handleBeforeUnload(event) {
      if (this.isDirty) {
        event.preventDefault();
        event.returnValue = "";
      }
    },

    handleUnitsSelected(chosenUnits) {
      settings.setUnits(chosenUnits);
      this.isUnitsModalVisible = false;
      if (this.activityData) {
        this.updateDataFields();
        this.updateWeatherDisplay();
      }
    },

    handleSelectionPropertyUpdate({ property, value }) {
      if (this.selection && this.selection.item) {
        this.selection.item[property] = value;
        const regenerationProperties = [
          "textColor",
          "transparentElementBg",
          "linkType",
          "customLink",
          "backgroundColor",
        ];
        if (regenerationProperties.includes(property)) {
          this.updateQrCodeValue(this.selection.item);
        }
      }
    },

    handleElementPropertyUpdate({ element, property, value }) {
      const itemToUpdate = this.findElementById(element.id);
      if (itemToUpdate) {
        itemToUpdate[property] = value;
        if (element.id.startsWith("qrCode_")) {
          if (property === "customLink" || property === "linkType") {
            this.updateQrCodeValue(itemToUpdate);
          }
        }
      }
    },

    handlePan(direction) {
      if (this.$refs.editorCanvas) {
        this.$refs.editorCanvas.panMap(direction);
      }
    },

    handleZoomIn() {
      if (this.$refs.editorCanvas) {
        this.$refs.editorCanvas.zoomIn();
      }
    },

    handleZoomOut() {
      if (this.$refs.editorCanvas) {
        this.$refs.editorCanvas.zoomOut();
      }
    },

    async handleSave(proceedToCheckout = false) {
      if (!auth.isLoggedIn) {
        notifyInfo("Please create an account to save your design.");
        localStorage.setItem("unsavedDesign", JSON.stringify(this.designState));
        localStorage.setItem("proceedToCheckout", proceedToCheckout);
        this.$router.push({
          name: "Register",
          query: { redirect: this.$route.fullPath },
        });
        return;
      }

      this.deselectAll();
      this.loading = true;

      const designDataPayload = {};
      const previewImagesPayload = {};
      const availablePlacements = Object.keys(
        this.editorProductData.print_areas
      );

      try {
        for (const placement of availablePlacements) {
          this.activePlacement = placement;
          await this.$nextTick();

          const canvasElement = this.$refs.editorCanvas.getCanvasElement();
          if (canvasElement) {
            const canvas = await html2canvas(canvasElement, {
              backgroundColor: null,
              useCORS: true,
              scale: 2,
            });
            previewImagesPayload[placement] = canvas.toDataURL("image/png");
          }

          designDataPayload[placement] = {
            mapSettings: JSON.parse(JSON.stringify(this.mapSettings)),
            mapElement: JSON.parse(JSON.stringify(this.mapElement)),
            dataFields: JSON.parse(JSON.stringify(this.dataFields)),
            graphElements: JSON.parse(JSON.stringify(this.graphElements)),
            textBoxes: JSON.parse(JSON.stringify(this.textBoxes)),
            photoElements: JSON.parse(JSON.stringify(this.photoElements)),
            badgeListElement: JSON.parse(JSON.stringify(this.badgeListElement)),
            qrCodeElements: JSON.parse(JSON.stringify(this.qrCodeElements)),
            weatherElement: JSON.parse(JSON.stringify(this.weatherElement)),
          };
        }

        const variantId = localStorage.getItem("selectedVariantId");
        const payload = {
          product_id: parseInt(this.productId),
          variant_id: parseInt(variantId),
          design_data: designDataPayload,
          preview_images: previewImagesPayload,
          name: `Design for ${this.activityData.details.name}`,
        };

        const response = await axios.post("/api/designs", payload, {
          withCredentials: true,
        });
        const newDesign = response.data;

        notifySuccess("Design saved successfully!");
        this.isDirty = false;

        if (proceedToCheckout) {
          this.$router.push({
            name: "Checkout",
            params: { designId: newDesign.id },
          });
        }
      } catch (error) {
        console.error("Error saving multi-part design:", error);
        notifyError("Failed to save design. Please try again.");
      } finally {
        this.loading = false;
      }
    },

    async fetchWeather() {
      if (!this.activityData?.details?.start_latlng?.length) return;
      const [lat, lon] = this.activityData.details.start_latlng;
      const startDate = new Date(this.activityData.details.start_date);
      const dateString = startDate.toISOString().split("T")[0];
      const apiUrl = `https://archive-api.open-meteo.com/v1/archive?latitude=${lat}&longitude=${lon}&start_date=${dateString}&end_date=${dateString}&hourly=temperature_2m,weathercode&timezone=auto`;
      try {
        const response = await axios.get(apiUrl);
        const hourlyData = response.data.hourly;
        let closestHourIndex = 0;
        let minDiff = Infinity;
        hourlyData.time.forEach((timeStr, index) => {
          const diff = Math.abs(new Date(timeStr) - startDate);
          if (diff < minDiff) {
            minDiff = diff;
            closestHourIndex = index;
          }
        });
        this.rawWeatherTemp =
          response.data.hourly.temperature_2m[closestHourIndex];
        const weatherCode = hourlyData.weathercode[closestHourIndex];
        const interpretation = this.getWeatherInterpretation(weatherCode);
        this.weatherData = {
          temp: 0,
          description: interpretation.description,
          icon: interpretation.icon,
        };
        this.updateWeatherDisplay();
      } catch (error) {
        console.error("Fout bij het ophalen van weerdata:", error);
        this.weatherData = null;
      }
    },

    updateWeatherDisplay() {
      if (this.rawWeatherTemp === null) return;
      if (settings.units === "imperial") {
        const fahrenheit = this.rawWeatherTemp * (9 / 5) + 32;
        this.weatherData.temp = Math.round(fahrenheit);
      } else {
        this.weatherData.temp = Math.round(this.rawWeatherTemp);
      }
    },

    getWeatherInterpretation(code) {
      const codes = {
        0: { description: "Clear sky", icon: "☀️" },
        1: { description: "Mainly clear", icon: "🌤️" },
        2: { description: "Partly cloudy", icon: "⛅️" },
        3: { description: "Overcast", icon: "☁️" },
        45: { description: "Fog", icon: "🌫️" },
        48: { description: "Depositing rime fog", icon: "🌫️" },
        51: { description: "Light drizzle", icon: "🌦️" },
        53: { description: "Moderate drizzle", icon: "🌦️" },
        55: { description: "Dense drizzle", icon: "🌦️" },
        56: { description: "Light freezing drizzle", icon: "🥶" },
        57: { description: "Dense freezing drizzle", icon: "🥶" },
        61: { description: "Slight rain", icon: "🌧️" },
        63: { description: "Moderate rain", icon: "🌧️" },
        65: { description: "Heavy rain", icon: "🌧️" },
        66: { description: "Light freezing rain", icon: "🥶" },
        67: { description: "Heavy freezing rain", icon: "🥶" },
        71: { description: "Slight snow fall", icon: "🌨️" },
        73: { description: "Moderate snow fall", icon: "🌨️" },
        75: { description: "Heavy snow fall", icon: "🌨️" },
        77: { description: "Snow grains", icon: "🌨️" },
        80: { description: "Slight rain showers", icon: "🌦️" },
        81: { description: "Moderate rain showers", icon: "🌧️" },
        82: { description: "Violent rain showers", icon: "🌧️" },
        85: { description: "Slight snow showers", icon: "🌨️" },
        86: { description: "Heavy snow showers", icon: "🌨️" },
        95: { description: "Thunderstorm", icon: "⛈️" },
        96: { description: "Thunderstorm with hail", icon: "⛈️" },
        99: { description: "Thunderstorm with heavy hail", icon: "⛈️" },
      };
      return codes[code] || { description: "Unknown", icon: "🤷" };
    },

    analyzeAchievements() {
      if (!this.activityData || !this.activityData.details) return;
      const details = this.activityData.details;
      const efforts = details.segment_efforts || [];
      const bestEfforts = details.best_efforts || [];
      let options = [];

      const getPriority = (type) =>
        ({
          kom: 1,
          qom: 1,
          top10: 2,
          pr_1: 3,
          pr_2: 4,
          pr_3: 5,
          best_effort_top3: 4,
          best_effort: 6,
        }[type] || 99);

      efforts.forEach((effort) => {
        if (!effort.achievements || effort.achievements.length === 0) return;
        const overallAchievement = effort.achievements.find(
          (a) => a.type === "overall"
        );
        const prAchievement = effort.achievements.find((a) => a.type === "pr");
        let text = "",
          type = "",
          priority = 99;

        if (overallAchievement) {
          if (overallAchievement.rank === 1) {
            type = details.athlete.sex === "F" ? "qom" : "kom";
            text = `${type.toUpperCase()} on '${
              effort.name
            }': ${this.formatEffortTime(effort.elapsed_time)} 👑`;
            priority = getPriority(type);
          } else if (overallAchievement.rank <= 10) {
            type = "top10";
            text = `${this.getOrdinal(overallAchievement.rank)} overall on '${
              effort.name
            }': ${this.formatEffortTime(effort.elapsed_time)} 🏆`;
            priority = getPriority(type);
          }
        } else if (prAchievement && prAchievement.rank <= 3) {
          const medals = ["🥇", "🥈", "🥉"];
          const medal = medals[prAchievement.rank - 1];
          type = `pr_${prAchievement.rank}`;

          if (prAchievement.rank === 1) {
            text = `Personal best on '${effort.name}': ${this.formatEffortTime(
              effort.elapsed_time
            )} ${medal}`;
          } else {
            text = `${this.getOrdinal(prAchievement.rank)} personal best on '${
              effort.name
            }': ${this.formatEffortTime(effort.elapsed_time)} ${medal}`;
          }

          priority = getPriority(type);
        }

        if (text) {
          options.push({ id: `segment_${effort.id}`, text, type, priority });
        }
      });

      bestEfforts.forEach((best) => {
        let text = "";
        let type = "best_effort";
        let priority = getPriority(type);
        const formattedValue = best.name.toLowerCase().includes("power")
          ? this.formatPower(best.average_watts)
          : this.formatEffortTime(best.elapsed_time);
        const rank = best.pr_rank;

        if (rank && rank >= 1 && rank <= 3) {
          const medal = ` ${["🥇", "🥈", "🥉"][rank - 1]}`;
          type = "best_effort_top3";
          priority = getPriority(`pr_${rank}`);
          if (rank === 1) {
            text = `Personal best ${best.name}: ${formattedValue}${medal}`;
          } else {
            text = `${this.getOrdinal(rank)} best ${
              best.name
            }: ${formattedValue}${medal}`;
          }
        } else {
          text = `Fastest ${best.name}: ${formattedValue}`;
        }

        options.push({
          id: `best_${best.id || best.name}`,
          text,
          type,
          priority,
        });
      });

      this.achievements = options
        .sort((a, b) => a.priority - b.priority)
        .map((opt, index) => ({ ...opt, selected: true, order: index }));
    },

    getAllVisibleElements() {
      const elements = [];
      if (this.mapElement.visible) elements.push(this.mapElement);
      if (this.dataFields.visible) elements.push(this.dataFields);
      if (this.badgeListElement.visible) elements.push(this.badgeListElement);
      if (this.weatherElement.visible) elements.push(this.weatherElement);
      elements.push(
        ...this.graphElements,
        ...this.textBoxes,
        ...this.photoElements,
        ...this.qrCodeElements
      );
      return elements;
    },

    bringToFront() {
      if (!this.activeElementObject) return;
      this.zIndexCounter++;
      this.activeElementObject.zIndex = this.zIndexCounter;
    },

    sendToBack() {
      if (!this.activeElementObject) return;
      const allElements = this.getAllVisibleElements();
      if (allElements.length < 2) return;
      const minZ = Math.min(...allElements.map((el) => el.zIndex));
      this.activeElementObject.zIndex = minZ - 1;
    },

    bringForward() {
      if (!this.activeElementObject) return;
      const sorted = this.getAllVisibleElements().sort(
        (a, b) => a.zIndex - b.zIndex
      );
      const currentIndex = sorted.findIndex(
        (el) => el.id === this.activeElementObject.id
      );
      if (currentIndex < sorted.length - 1) {
        const elAbove = sorted[currentIndex + 1];
        [this.activeElementObject.zIndex, elAbove.zIndex] = [
          elAbove.zIndex,
          this.activeElementObject.zIndex,
        ];
      }
    },

    sendBackward() {
      if (!this.activeElementObject) return;
      const sorted = this.getAllVisibleElements().sort(
        (a, b) => a.zIndex - b.zIndex
      );
      const currentIndex = sorted.findIndex(
        (el) => el.id === this.activeElementObject.id
      );
      if (currentIndex > 0) {
        const elBelow = sorted[currentIndex - 1];
        [this.activeElementObject.zIndex, elBelow.zIndex] = [
          elBelow.zIndex,
          this.activeElementObject.zIndex,
        ];
      }
    },

    clearCanvas() {
      if (
        !confirm(
          "Are you sure you want to clear the canvas? This cannot be undone."
        )
      )
        return;
      localStorage.removeItem("autosavedDesign");
      this.isApplyingState = true;

      this.mapElement.visible = false;
      this.dataFields.visible = false;
      this.badgeListElement.visible = false;
      this.weatherElement.visible = false;
      this.graphElements = [];
      this.textBoxes = [];
      this.photoElements = [];
      this.qrCodeElements = [];

      this.deselectAll();
      this.clipboard = null;

      this.$nextTick(() => {
        const clearedState = JSON.parse(JSON.stringify(this.designState));
        this.history = [clearedState];
        this.historyIndex = 0;
        this.isApplyingState = false;
      });
    },

    deleteSelectedElement() {
      const elementToDelete = this.activeElementObject;
      if (!elementToDelete) return;
      this.removeElement(elementToDelete);
    },

    copyElement() {
      if (!this.activeElementObject) return;
      this.clipboard = {
        type: this.selectedElement,
        element: JSON.parse(JSON.stringify(this.activeElementObject)),
      };
    },

    cutElement() {
      this.copyElement();
      this.deleteSelectedElement();
    },

    pasteElement() {
      if (!this.clipboard) return;
      const newElement = JSON.parse(JSON.stringify(this.clipboard.element));

      const collections = {
        graph: this.graphElements,
        textBox: this.textBoxes,
        photo: this.photoElements,
        qrCode: this.qrCodeElements,
      };
      const collection = collections[this.clipboard.type];
      if (collection) {
        newElement.id = `${this.clipboard.type}_${Date.now()}`;
        newElement.x += 20;
        newElement.y += 20;
        newElement.zIndex = ++this.zIndexCounter;
        collection.push(newElement);
        this.$nextTick(() =>
          this.selectElement(this.clipboard.type, newElement)
        );
      }
    },

    handleKeyDown(event) {
      const activeEl = document.activeElement;
      if (["INPUT", "TEXTAREA"].includes(activeEl.tagName)) return;

      const isMac = navigator.platform.toUpperCase().indexOf("MAC") >= 0;
      const ctrlOrCmd = isMac ? event.metaKey : event.ctrlKey;

      if (
        ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)
      ) {
        event.preventDefault();
        if (!this.activeElementObject) return;
        const amount = event.shiftKey ? 10 : 1;
        const el = this.activeElementObject;
        if (event.key === "ArrowUp") el.y -= amount;
        if (event.key === "ArrowDown") el.y += amount;
        if (event.key === "ArrowLeft") el.x -= amount;
        if (event.key === "ArrowRight") el.x += amount;
      } else if (ctrlOrCmd && event.key.toLowerCase() === "z") {
        event.preventDefault();
        this.undo();
      } else if (ctrlOrCmd && event.key.toLowerCase() === "y") {
        event.preventDefault();
        this.redo();
      } else if (ctrlOrCmd && event.key.toLowerCase() === "c") {
        event.preventDefault();
        this.copyElement();
      } else if (ctrlOrCmd && event.key.toLowerCase() === "x") {
        event.preventDefault();
        this.cutElement();
      } else if (ctrlOrCmd && event.key.toLowerCase() === "v") {
        event.preventDefault();
        this.pasteElement();
      } else if (event.key === "Delete" || event.key === "Backspace") {
        event.preventDefault();
        this.deleteSelectedElement();
      } else if (event.key === "Escape") {
        event.preventDefault();
        this.deselectAll();
      }
    },

    loadState(state) {
      this.isApplyingState = true;
      Object.assign(this.mapSettings, state.mapSettings);
      Object.assign(this.mapElement, state.mapElement);
      Object.assign(this.dataFields, state.dataFields);
      this.graphElements = state.graphElements || [];
      this.textBoxes = state.textBoxes || [];
      this.photoElements = state.photoElements || [];
      Object.assign(this.badgeListElement, state.badgeListElement);
      this.qrCodeElements = state.qrCodeElements || [];
      Object.assign(this.weatherElement, state.weatherElement);
      this.$nextTick(() => {
        this.isApplyingState = false;
      });
    },

    undo() {
      if (!this.canUndo) return;
      this.historyIndex--;
      this.loadState(this.history[this.historyIndex]);
    },

    redo() {
      if (!this.canRedo) return;
      this.historyIndex++;
      this.loadState(this.history[this.historyIndex]);
    },

    alignElement(direction) {
      const el = this.activeElementObject;
      const canvas = this.$refs.editorCanvas.getCanvasElement();
      if (!el || !canvas) return;
      const canvasRect = canvas.getBoundingClientRect();
      switch (direction) {
        case "left":
          el.x = -(canvasRect.width / 2) + el.width / 2;
          break;
        case "center-h":
          el.x = 0;
          break;
        case "right":
          el.x = canvasRect.width / 2 - el.width / 2;
          break;
        case "top":
          el.y = -(canvasRect.height / 2) + el.height / 2;
          break;
        case "center-v":
          el.y = 0;
          break;
        case "bottom":
          el.y = canvasRect.height / 2 - el.height / 2;
          break;
      }
    },

    async updateQrCodeValue(qrCode) {
      if (!qrCode || !this.activityData) return;
      let url = "";
      if (qrCode.linkType === "activity")
        url = `https://www.strava.com/activities/${this.activityData.details.id}`;
      else if (qrCode.linkType === "profile")
        url = `https://www.strava.com/athletes/${this.activityData.details.athlete.id}`;
      else if (qrCode.linkType === "custom") url = qrCode.customLink;

      const lightColorForQr = qrCode.transparentElementBg
        ? "#0000"
        : qrCode.backgroundColor;

      if (url) {
        try {
          qrCode.dataUrl = await QRCode.toDataURL(url, {
            errorCorrectionLevel: "H",
            margin: 1,
            width: 256,
            color: {
              dark: qrCode.textColor,
              light: lightColorForQr,
            },
          });
        } catch (err) {
          qrCode.dataUrl = null;
        }
      } else {
        qrCode.dataUrl = null;
      }
    },

    selectElement(type, item = null) {
      const creatableTypes = {
        graph: this.graphElements,
        textBox: this.textBoxes,
        photo: this.photoElements,
        qrCode: this.qrCodeElements,
      };

      if (creatableTypes[type] && !item) {
        const collection = creatableTypes[type];
        if (collection.length === 0) {
          this.addElement(type);
          return;
        } else {
          item = collection[0];
        }
      }

      if (type === "dataFields") {
        if (!this.dataFields.visible) {
          this.dataFields.x = 0;
          this.dataFields.y = 0;
        }
        this.dataFields.visible = true;
      }

      if (type === "map") {
        this.mapElement.visible = true;
      }

      if (type === "badgeList" && this.achievements.length > 0) {
        this.badgeListElement.visible = true;
      }

      if (type === "weather" && this.weatherData) {
        if (!this.weatherElement.visible) {
          this.weatherElement.x = 0;
          this.weatherElement.y = 0;
        }
        this.weatherElement.visible = true;
      }

      this.selection.type = type;
      this.selection.item = item;
      const element = this.activeElementObject;
      if (element && typeof element.zIndex !== "undefined") {
        this.zIndexCounter = Math.max(this.zIndexCounter, element.zIndex);
        element.zIndex = ++this.zIndexCounter;
      }
    },

    deselectAll() {
      this.selection.type = null;
      this.selection.item = null;
    },

    updateElementGeometry({ element, newGeometry }) {
      const originalElement = this.findElementById(element.id);
      if (originalElement) {
        Object.assign(originalElement, newGeometry);
      }
    },

    findElementById(id) {
      const allElements = [
        this.mapElement,
        this.dataFields,
        this.badgeListElement,
        this.weatherElement,
        ...this.graphElements,
        ...this.textBoxes,
        ...this.photoElements,
        ...this.qrCodeElements,
      ];
      return allElements.find((el) => el && el.id === id);
    },

    addElement(type) {
      if (type === "graph") {
        if (this.graphElements.length >= 3) return;
        const newGraph = {
          id: `graph_${Date.now()}`,
          visible: true,
          x: 0 + this.graphElements.length * 20,
          y: 0 + this.graphElements.length * 20,
          width: 350,
          height: 200,
          zIndex: ++this.zIndexCounter,
          selectedDataSource: "heartrate",
          lineColor: "#fc4c02",
          fillColor: "#fca587",
          transparentFill: false,
          transparentBg: true,
          lineThickness: 2,
          showAltitudeInBackground: false,
          showXAxisTitle: true,
          showXAxisLabels: true,
          showYAxisTitle: true,
          showYAxisLabels: true,
          showY1AxisTitle: true,
          showY1AxisLabels: true,
          showGrid: true,
          axisColor: this.getInitialElementColor("label"),
          showLegend: false,
          xAxisTicks: 10,
          yAxisTicks: 8,
          tickFontSize: 12,
          titleFontSize: 13,
          yAxisMin: null,
          yAxisMax: null,
        };
        this.graphElements.push(newGraph);
        this.selectElement("graph", newGraph);
        return;
      }

      const defaults = {
        textBox: {
          text: this.activityData?.details?.name || "Your Title Here",
          x: 0,
          y: 0,
          width: 300,
          height: 80,
          fontFamily: "Arial",
          fontSize: 30,
          fontColor: this.getInitialElementColor(),
          textAlign: "center",
          isBold: false,
          isItalic: false,
          transparentBg: true,
          backgroundColor: "#ffffff",
          borderRadius: 7,
        },
        photo: {
          src: null,
          x: 0,
          y: 0,
          width: 300,
          height: 200,
          mask: "none",
          filter: "none",
        },
        graph: {
          visible: true,
          x: 100,
          y: 100,
          width: 400,
          height: 200,
          selectedDataSource: "heartrate",
          lineColor: "#fc4c02",
          fillColor: "#fca587",
          showGrid: true,
          xAxisTicks: 10,
          yAxisTicks: 8,
          showLegend: false,
          yAxisTitle: "Heart Rate",
          xAxisTitle: "Distance",
          showAltitudeInBackground: false,
          transparentBg: true,
          transparentFill: false,
          showXAxisTitle: true,
          showXAxisLabels: true,
          showYAxisTitle: true,
          showYAxisLabels: true,
          lineThickness: 2,
          tickFontSize: 12,
          zIndex: this.zIndexCounter++,
        },
        qrCode: {
          x: 0,
          y: 0,
          width: 350,
          height: 120,
          linkType: "activity",
          customLink: "",
          dataUrl: null,
          showText: true,
          text: "Give me Kudos!",
          transparentElementBg: true,
          backgroundColor: "#ffffff",
          fontFamily: "Arial",
          fontSize: 24,
          textColor: this.getInitialElementColor(),
          borderRadius: 8,
          borderWidth: 0,
          borderColor: this.getInitialElementColor(),
        },
      };
      if (!defaults[type]) return;
      const newElement = {
        id: `${type}_${Date.now()}`,
        ...defaults[type],
        zIndex: ++this.zIndexCounter,
      };
      if (type === "qrCode") {
        this.updateQrCodeValue(newElement);
      }
      const collectionMap = {
        textBox: this.textBoxes,
        photo: this.photoElements,
        qrCode: this.qrCodeElements,
      };
      collectionMap[type].push(newElement);
      this.selectElement(type, newElement);
    },

    removeElement(elementToRemove) {
      if (!elementToRemove || !elementToRemove.id) return;
      const type = elementToRemove.id.split("_")[0];
      const collections = {
        graph: this.graphElements,
        textBox: this.textBoxes,
        photo: this.photoElements,
        qrCode: this.qrCodeElements,
      };
      if (collections[type]) {
        const collection = collections[type];
        const index = collection.findIndex(
          (item) => item.id === elementToRemove.id
        );
        if (index > -1) {
          collection.splice(index, 1);
        }
      } else if (this.elementKeyMap[type]) {
        const key = this.elementKeyMap[type];
        this[key].visible = false;
      }
      this.deselectAll();
    },

    getOrdinal(n) {
      const s = ["th", "st", "nd", "rd"];
      const v = n % 100;
      return n + (s[(v - 20) % 10] || s[v] || s[0]);
    },

    formatEffortTime(seconds) {
      return new Date(seconds * 1000).toISOString().substr(11, 8);
    },

    formatDistance(m) {
      if (m === undefined) return "-";
      if (settings.units === "imperial") {
        const miles = m * 0.000621371;
        return `${miles.toFixed(2)} mi`;
      }
      return `${(m / 1000).toFixed(2)} km`;
    },

    formatTime(s) {
      return s === undefined
        ? "-"
        : new Date(s * 1000).toISOString().substr(11, 8);
    },

    formatPace(sPerKm) {
      if (sPerKm === undefined || !isFinite(sPerKm)) return "-";
      if (settings.units === "imperial") {
        const sPerMile = sPerKm * 1.60934;
        const minutes = Math.floor(sPerMile / 60);
        const seconds = Math.round(sPerMile % 60)
          .toString()
          .padStart(2, "0");
        return `${minutes}:${seconds} /mi`;
      }
      const minutes = Math.floor(sPerKm / 60);
      const seconds = Math.round(sPerKm % 60)
        .toString()
        .padStart(2, "0");
      return `${minutes}:${seconds} /km`;
    },

    formatSpeed(mps) {
      if (mps === undefined) return "-";
      if (settings.units === "imperial") {
        const mph = mps * 2.23694;
        return `${mph.toFixed(1)} mph`;
      }
      return `${(mps * 3.6).toFixed(1)} km/h`;
    },

    formatElevation(m) {
      if (m === undefined) return "-";
      if (settings.units === "imperial") {
        const feet = m * 3.28084;
        return `${Math.round(feet)} ft`;
      }
      return `${Math.round(m)} m`;
    },

    formatHeartRate(bpm) {
      return bpm === undefined ? "-" : `${Math.round(bpm)} bpm`;
    },

    formatCadence(spm) {
      return spm === undefined ? "-" : `${Math.round(spm)} spm`;
    },

    formatPower(w) {
      return w === undefined ? "-" : `${Math.round(w)} W`;
    },

    updateDataFields() {
      if (!this.activityData || !this.activityData.details) return;
      const data = this.activityData.details;
      this.dataFields.availableFields.forEach((field) => {
        const formatters = {
          distance: this.formatDistance(data.distance),
          time: this.formatTime(data.moving_time),
          moving_time: this.formatTime(data.moving_time),
          elapsed_time: this.formatTime(data.elapsed_time),
          elevation_gain: this.formatElevation(data.total_elevation_gain),
          max_elevation: this.formatElevation(data.elev_high),
          avg_pace: this.formatPace(1000 / data.average_speed),
          max_pace: this.formatPace(1000 / data.max_speed),
          avg_speed: this.formatSpeed(data.average_speed),
          max_speed: this.formatSpeed(data.max_speed),
          avg_hr: this.formatHeartRate(data.average_heartrate),
          max_hr: this.formatHeartRate(data.max_heartrate),
          avg_cadence: this.formatCadence(
            data.average_cadence ? data.average_cadence * 2 : undefined
          ),
          max_cadence: this.formatCadence(
            data.max_cadence ? data.max_cadence * 2 : undefined
          ),
          avg_power: this.formatPower(data.average_watts),
          max_power: this.formatPower(data.max_watts),
        };
        field.value = formatters[field.id] || "-";
      });
    },
  },

  async mounted() {
    this.loading = true;

    localStorage.setItem("selectedProductId", this.productId);

    window.addEventListener("beforeunload", this.handleBeforeUnload);
    window.addEventListener("keydown", this.handleKeyDown);

    if (!localStorage.getItem("user-units")) {
      this.isUnitsModalVisible = true;
    }

    try {
      let activityRes;
      if (this.activityId === "gpx" && window.tempGpxData) {
        activityRes = { data: window.tempGpxData };
        delete window.tempGpxData;
      }

      const [productRes, finalActivityRes] = await Promise.all([
        axios.get(`/api/products/${this.productId}`, {
          withCredentials: true,
        }),
        activityRes ||
          axios.get(`/api/activities/${this.activityId}`, {
            withCredentials: true,
          }),
      ]);

      this.editorProductData = productRes.data;
      this.activityData = finalActivityRes.data;
      this.dataFields.labelColor = this.getInitialElementColor("label");
      this.dataFields.valueColor = this.getInitialElementColor("main");
      this.badgeListElement.textColor = this.getInitialElementColor("main");
      this.weatherElement.textColor = this.getInitialElementColor("main");
      this.activityPhotos = finalActivityRes.data.photos || [];

      if (this.activityData && this.activityData.details.athlete?.id) {
        try {
          const statsRes = await axios.get(
            `/api/athlete-stats/${this.activityData.details.athlete.id}`
          );
          this.athleteStats = statsRes.data;
          this.analyzeAchievements();
        } catch (statsError) {
          console.error("Fout bij ophalen atleetstatistieken:", statsError);
        }
      }

      const designIdToLoad = this.designId || this.$route.query.design_id;
      const unsavedDesign = localStorage.getItem("autosavedDesign");

      if (designIdToLoad) {
        const res = await axios.get(`/api/designs/${designIdToLoad}`, {
          withCredentials: true,
        });
        this.loadState(res.data.design_data);
      } else if (unsavedDesign) {
        this.loadState(JSON.parse(unsavedDesign));
      }
    } catch (error) {
      console.error("Fout bij het laden van de editor data:", error);
      notifyError("Er is iets misgegaan bij het laden van de editor.");
    } finally {
      this.mapElement.visible = true;
      this.history.push(this.designState);
      this.historyIndex = 0;
      this.loading = false;
    }
  },

  beforeUnmount() {
    window.removeEventListener("keydown", this.handleKeyDown);
    window.removeEventListener("beforeunload", this.handleBeforeUnload);
  },

  beforeRouteLeave(to, from, next) {
    if (this.isDirty) {
      const answer = window.confirm(
        "You have unsaved changes. Are you sure you want to leave this page?"
      );
      if (answer) {
        next();
      } else {
        next(false);
      }
    } else {
      next();
    }
  },
};
</script>

<style scoped>
.editor-main-area {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  min-width: 0;
  min-height: 0;
}

.sidebar-button {
  display: block;
  width: 100%;
  box-sizing: border-box;
  margin-top: 10px;
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  color: white;
  font-weight: bold;
  font-size: 0.9em;
  cursor: pointer;
  text-align: center;
  transition: background-color 0.2s;
}

.reset-button {
  background-color: #6c757d;
}

.reset-button:hover {
  background-color: #5a6268;
}

.remove-button {
  background-color: #dc3545;
}

.remove-button:hover {
  background-color: #c82333;
}

.add-button {
  background-color: #28a745;
}

.add-button:hover {
  background-color: #218838;
}

.design-editor-page {
  display: flex;
  height: calc(100vh - 60px);
  font-family: "Inter", sans-serif;
  background-color: #f0f2f5;
}
</style>
