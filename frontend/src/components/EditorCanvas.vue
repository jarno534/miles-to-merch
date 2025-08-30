<template>
  <div
    class="editor-canvas-container"
    @mouseup="stopInteraction"
    @mouseleave="stopInteraction"
    @mousemove="handleInteraction"
    @dragover.prevent
  >
    <div v-if="loading" class="loading-message">
      <p>Loading activity data...</p>
    </div>
    <div v-else class="editor-canvas">
      <div
        class="tshirt-mockup"
        ref="tshirtMockup"
        :style="mockupStyle"
        @click="$emit('deselect-all')"
      >
        <div
          v-if="mapElement.visible"
          :class="['design-area', { selected: selection.type === 'map' }]"
          :style="mapElementStyle"
          @mousedown.prevent="startDrag($event, mapElement)"
          @click.stop="$emit('select-element', 'map', mapElement)"
        >
          <div
            v-show="!is3DMode"
            id="map-leaflet"
            ref="mapContainer2D"
            class="map-container-base"
            :style="[mapContainerStyle, fadeMaskStyle]"
          ></div>
          <div
            v-show="is3DMode"
            id="map-maplibre"
            ref="mapContainer3D"
            class="map-container-base"
            :style="[mapContainerStyle, fadeMaskStyle]"
          ></div>

          <div
            v-if="mapSettings.gradientData !== 'none' && !is3DMode"
            class="map-legend"
          >
            <span class="legend-gradient" :style="legendGradientStyle"></span>
            <span class="legend-label">{{ currentLegendLabel }}</span>
          </div>
          <template v-if="selection.type === 'map'">
            <div
              v-for="handle in resizeHandles"
              :key="handle"
              :class="`resize-handle ${handle}`"
              @mousedown.stop.prevent="startResize($event, mapElement, handle)"
            ></div>
          </template>
        </div>

        <div
          v-if="dataFields.visible"
          :class="[
            'design-area',
            'data-field-area',
            { selected: selection.type === 'dataFields' },
          ]"
          :style="[dataFieldsStyle, containerBorderStyle]"
          @mousedown.prevent="startDrag($event, dataFields)"
          @click.stop="$emit('select-element', 'dataFields', dataFields)"
        >
          <div class="data-grid" :style="dataGridStyle">
            <div
              v-for="(field, index) in selectedDataFields"
              :key="field.id"
              class="data-cell"
              :style="getCellBorderStyle(index)"
            >
              <span
                class="data-label"
                :style="{
                  fontSize: `${dataFields.labelSize}px`,
                  color: dataFields.labelColor,
                }"
                >{{ field.label }}</span
              >
              <span
                class="data-value"
                :style="{
                  fontSize: `${dataFields.valueSize}px`,
                  color: dataFields.valueColor,
                }"
                >{{ field.value }}</span
              >
            </div>
          </div>
          <template v-if="selection.type === 'dataFields'">
            <div
              v-for="handle in resizeHandles"
              :key="handle"
              :class="`resize-handle ${handle}`"
              @mousedown.stop.prevent="startResize($event, dataFields, handle)"
            ></div>
          </template>
        </div>

        <div
          v-for="graph in graphElements"
          :key="graph.id"
          :class="[
            'design-area',
            {
              selected: selection.item && selection.item.id === graph.id,
              'is-transparent': graph.transparentBg,
            },
          ]"
          :style="getGraphElementStyle(graph)"
          @mousedown.prevent="startDrag($event, graph)"
          @click.stop="$emit('select-element', 'graph', graph)"
        >
          <GraphComponent
            v-if="activityData"
            :activity-data="activityData"
            :options="graph"
            @autorange-updated="
              $emit('update-graph-autorange', { graph, range: $event })
            "
          />
          <template v-if="selection.item && selection.item.id === graph.id">
            <div
              v-for="handle in resizeHandles"
              :key="handle"
              :class="`resize-handle ${handle}`"
              @mousedown.stop.prevent="startResize($event, graph, handle)"
            ></div>
          </template>
        </div>

        <div
          v-for="box in textBoxes"
          :key="box.id"
          :class="[
            'design-area',
            { selected: selection.item && selection.item.id === box.id },
          ]"
          :style="getTextBoxStyle(box)"
          @mousedown.prevent="startDrag($event, box)"
          @click.stop="$emit('select-element', 'textBox', box)"
        >
          <div class="editable-text" :style="getEditableTextStyle(box)">
            {{ box.text }}
          </div>
          <template v-if="selection.item && selection.item.id === box.id">
            <div
              v-for="handle in resizeHandles"
              :key="handle"
              :class="`resize-handle ${handle}`"
              @mousedown.stop.prevent="startResize($event, box, handle)"
            ></div>
          </template>
        </div>

        <div
          v-for="photo in photoElements"
          :key="photo.id"
          :class="[
            'design-area',
            { selected: selection.item && selection.item.id === photo.id },
          ]"
          :style="getPhotoElementStyle(photo)"
          @mousedown.prevent="startDrag($event, photo)"
          @click.stop="$emit('select-element', 'photo', photo)"
        >
          <div v-if="!photo.src" class="photo-placeholder">Select a photo</div>
          <img
            v-if="photo.src"
            :src="photo.src"
            :style="{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              filter: photo.filter || 'none',
            }"
          />
          <template v-if="selection.item && selection.item.id === photo.id">
            <div
              v-for="handle in resizeHandles"
              :key="handle"
              :class="`resize-handle ${handle}`"
              @mousedown.stop.prevent="startResize($event, photo, handle)"
            ></div>
          </template>
        </div>

        <div
          v-if="badgeListElement.visible"
          :class="[
            'design-area',
            'badge-list-area',
            {
              selected: selection.type === 'badgeList',
              'is-transparent': badgeListElement.transparentBg,
            },
          ]"
          :style="getBadgeListStyle"
          @mousedown.prevent="startDrag($event, badgeListElement)"
          @click.stop="$emit('select-element', 'badgeList', badgeListElement)"
        >
          <div class="badge-list-content">
            <p
              v-for="badge in visibleBadges"
              :key="badge.id"
              class="badge-list-item"
            >
              {{ badge.text }}
            </p>
          </div>
          <template v-if="selection.type === 'badgeList'">
            <div
              v-for="handle in resizeHandles"
              :key="handle"
              :class="`resize-handle ${handle}`"
              @mousedown.stop.prevent="
                startResize($event, badgeListElement, handle)
              "
            ></div>
          </template>
        </div>

        <div
          v-for="qrCode in qrCodeElements"
          :key="qrCode.id"
          :class="[
            'design-area',
            'qr-code-area',
            {
              selected: selection.item && selection.item.id === qrCode.id,
              'is-transparent': qrCode.transparentBg,
            },
          ]"
          :style="getQrCodeElementStyle(qrCode)"
          @mousedown.prevent="startDrag($event, qrCode)"
          @click.stop="$emit('select-element', 'qrCode', qrCode)"
        >
          <div class="qr-code-wrapper">
            <img
              v-if="qrCode.dataUrl"
              :src="qrCode.dataUrl"
              class="qr-image"
              alt="QR Code"
            />
            <div
              v-else-if="qrCode.linkType === 'custom' && !qrCode.customLink"
              class="photo-placeholder"
            >
              Enter a URL
            </div>
            <div v-else class="photo-placeholder">Generating QR...</div>
            <div v-if="qrCode.showText" class="qr-text-container">
              <textarea
                v-if="selection.item && selection.item.id === qrCode.id"
                class="qr-text-input"
                v-model="qrCode.text"
                @blur="logQrTextUpdate(qrCode)"
                @click.stop
                :style="getQrTextStyle(qrCode)"
              ></textarea>
              <span v-else class="qr-text" :style="getQrTextStyle(qrCode)">{{
                qrCode.text
              }}</span>
            </div>
          </div>
          <template v-if="selection.item && selection.item.id === qrCode.id">
            <div
              v-for="handle in resizeHandles"
              :key="handle"
              :class="`resize-handle ${handle}`"
              @mousedown.stop.prevent="startResize($event, qrCode, handle)"
            ></div>
          </template>
        </div>

        <div
          v-if="weatherElement.visible"
          :class="[
            'design-area',
            'weather-area',
            {
              selected: selection.type === 'weather',
              'is-transparent': weatherElement.transparentBg,
            },
          ]"
          :style="{
            transform: `translate(-50%, -50%) translate(${weatherElement.x}px, ${weatherElement.y}px)`,
            width: `${weatherElement.width}px`,
            height: `${weatherElement.height}px`,
            zIndex: weatherElement.zIndex,
            color: weatherElement.textColor,
            fontSize: `${weatherElement.fontSize}px`,
            backgroundColor: weatherElement.transparentBg
              ? 'transparent'
              : weatherElement.backgroundColor,
            cursor:
              activeInteraction.element?.id === weatherElement.id
                ? 'grabbing'
                : 'grab',
            borderRadius: `${weatherElement.borderRadius || 0}px`,
            overflow: weatherElement.borderRadius > 0 ? 'hidden' : 'visible',
          }"
          @mousedown.prevent="startDrag($event, weatherElement)"
          @click.stop="$emit('select-element', 'weather', weatherElement)"
        >
          <div v-if="weatherData" class="weather-content">
            <span v-if="weatherElement.showIcon" class="weather-icon-emoji">{{
              weatherData.icon
            }}</span>
            <div class="weather-details">
              <span class="weather-temp">{{ weatherData.temp }}&deg;C</span>
              <span class="weather-desc">{{ weatherData.description }}</span>
            </div>
          </div>
          <template v-if="selection.type === 'weather'">
            <div
              v-for="handle in resizeHandles"
              :key="handle"
              :class="`resize-handle ${handle}`"
              @mousedown.stop.prevent="
                startResize($event, weatherElement, handle)
              "
            ></div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { toRaw } from "vue";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import GraphComponent from "@/components/GraphComponent.vue";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { TILE_LAYERS } from "@/config/mapConfig.js";

const gradientColorSchemes = {
  velocity_smooth: { label: "Speed", min: "#a3d5ff", max: "#003b80" },
  heartrate: { label: "Heart Rate", min: "#ffc4c4", max: "#7a0000" },
  altitude: { label: "Altitude", min: "#d8c3a5", max: "#4a3728" },
  distance: { label: "Time", min: "#ffe3b3", max: "#e67300" },
  watts: { label: "Power", min: "#e6c6ff", max: "#4b0082" },
};

export default {
  name: "EditorCanvas",
  components: { GraphComponent },
  props: {
    editorProductData: {
      type: Object,
      default: null,
    },
    selection: {
      type: Object,
      required: true,
      default: () => ({ type: null, item: null }),
    },
    loading: Boolean,
    activityData: Object,
    mapElement: Object,
    mapSettings: Object,
    dataFields: Object,
    graphElements: Array,
    textBoxes: Array,
    photoElements: Array,
    badgeListElement: Object,
    achievements: Array,
    qrCodeElements: Array,
    weatherElement: Object,
    weatherData: Object,
  },
  emits: [
    "select-element",
    "deselect-all",
    "update-element-geometry",
    "update-map-instance",
    "update-graph-autorange",
    "update-element-property",
  ],

  data() {
    return {
      routeBounds: null,
      routeCenter: null,
      currentTileLayer: null,
      mapPolylines: [],
      activeInteraction: { element: null, type: null, direction: null },
      initialMouse: { x: 0, y: 0 },
      initialElementState: { x: 0, y: 0, width: 0, height: 0 },
      minSize: 50,
      resizeHandles: [
        "top-left",
        "top",
        "top-right",
        "right",
        "bottom-right",
        "bottom",
        "bottom-left",
        "left",
      ],
    };
  },

  computed: {
    mockupStyle() {
      console.log(
        "%c[EditorCanvas] mockupStyle wordt berekend. Ontvangen props:",
        "color: #fc4c02; font-weight: bold;",
        this.editorProductData
      );
      if (
        this.editorProductData &&
        this.editorProductData.print_areas &&
        this.editorProductData.print_areas.front
      ) {
        return {
          backgroundImage: `url(${this.editorProductData.print_areas.front.url})`,
          backgroundColor: "transparent",
        };
      }
      console.log(
        "%c[EditorCanvas] Voorwaarden voor mockupStyle NIET voldaan. Lege stijl.",
        "color: red; font-weight: bold;"
      );
      return {};
    },
    is3DMode() {
      const styleKey = this.mapSettings.style;
      return TILE_LAYERS[styleKey] && TILE_LAYERS[styleKey].is3D;
    },

    mapElementStyle() {
      const el = this.mapElement;
      return {
        transform: `translate(-50%, -50%) translate(${el.x}px, ${el.y}px)`,
        width: `${el.width}px`,
        height: `${el.height}px`,
        zIndex: el.zIndex,
        cursor:
          this.activeInteraction.element?.id === el.id ? "grabbing" : "grab",
      };
    },

    dataFieldsStyle() {
      const el = this.dataFields;
      return {
        transform: `translate(-50%, -50%) translate(${el.x}px, ${el.y}px)`,
        width: `${el.width}px`,
        height: `${el.height}px`,
        zIndex: el.zIndex,
        cursor:
          this.activeInteraction.element?.id === el.id ? "grabbing" : "grab",
      };
    },

    containerBorderStyle() {
      const { borderStyle, borderColor } = this.dataFields;
      if (borderStyle === "outer" || borderStyle === "all") {
        return { border: `1.5px solid ${borderColor}` };
      }
      return {};
    },

    dataGridStyle() {
      return { gridTemplateColumns: `repeat(${this.dataFields.columns}, 1fr)` };
    },

    selectedDataFields() {
      if (!this.dataFields || !this.dataFields.availableFields) return [];
      return this.dataFields.availableFields
        .filter((field) => field.selected)
        .sort((a, b) => a.order - b.order);
    },

    mapContainerStyle() {
      const style = { width: "100%", height: "100%" };
      if (this.mapSettings.style === "none") {
        return { ...style, backgroundColor: "transparent" };
      }
      const visuals = {
        grayscale: "grayscale(100%)",
        blue: "sepia(100%) hue-rotate(180deg)",
        pink: "sepia(50%) hue-rotate(300deg) saturate(150%)",
        sepia: "sepia(100%)",
        vivid: "saturate(200%)",
      };
      style.filter = visuals[this.mapSettings.visuals] || "";
      return style;
    },

    fadeMaskStyle() {
      if (!this.mapSettings.fadeEdges) return {};
      const maskImage = `
        linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%),
        linear-gradient(to bottom, transparent 0%, black 10%, black 90%, transparent 100%)
      `;
      return {
        maskImage,
        WebkitMaskImage: maskImage,
        maskComposite: "intersect",
        WebkitMaskComposite: "source-in",
      };
    },

    legendGradientStyle() {
      const scheme = gradientColorSchemes[this.mapSettings.gradientData];
      if (!scheme) return {};
      return {
        background: `linear-gradient(to right, ${scheme.min}, ${scheme.max})`,
      };
    },

    currentLegendLabel() {
      const scheme = gradientColorSchemes[this.mapSettings.gradientData];
      return scheme ? scheme.label : "";
    },

    getBadgeListStyle() {
      const el = this.badgeListElement;
      const style = {
        transform: `translate(-50%, -50%) translate(${el.x}px, ${el.y}px)`,
        width: `${el.width}px`,
        height: `${el.height}px`,
        color: el.textColor,
        fontSize: `${el.fontSize}px`,
        fontFamily: el.fontFamily,
        backgroundColor: el.transparentBg ? "transparent" : el.backgroundColor,
        zIndex: el.zIndex,
        cursor:
          this.activeInteraction.element?.id === el.id ? "grabbing" : "grab",
      };
      if (el.borderEnabled) {
        style.border = `${el.borderWidth}px solid ${el.borderColor}`;
      }
      return style;
    },

    visibleBadges() {
      const gefilterd = this.achievements.filter((a) => a.selected);
      const gesorteerd = [...gefilterd].sort((a, b) => a.order - b.order);
      return gesorteerd;
    },
  },

  watch: {
    loading(isLoading, wasLoading) {
      if (wasLoading && !isLoading) {
        this.$nextTick(() => {
          this.initializeMap();
        });
      }
    },
    "mapSettings.pitch"() {
      this.updateCamera3D();
    },
    "mapSettings.bearing"() {
      this.updateCamera3D();
    },
    "mapSettings.style"() {
      this.initializeMap();
    },
    "mapSettings.visuals": "updateMapTileLayer",
    "mapSettings.lineColor": "updateMap",
    "mapSettings.lineWeight": "updateMap",
    "mapSettings.gradientData": "updateMap",
    "mapSettings.showStartEndMarkers": "updateStartEndMarkers",

    "mapElement.width"() {
      this.$nextTick(() => {
        this.map2DInstance?.invalidateSize();
        this.map3DInstance?.resize();
      });
    },
    "mapElement.height"() {
      this.$nextTick(() => {
        this.map2DInstance?.invalidateSize();
        this.map3DInstance?.resize();
      });
    },
    selection: {
      handler(newSelection) {
        if (newSelection.type === "map") {
          this.$nextTick(() => {
            this.map2DInstance?.invalidateSize();
            this.map3DInstance?.resize();
          });
        }
      },
      deep: true,
    },
  },

  methods: {
    logQrTextUpdate(qrCode) {
      const payload = {
        element: qrCode,
        property: "text",
        value: qrCode.text,
      };
      console.log(
        "%c[EditorCanvas] @blur: Event wordt verstuurd...",
        "color: blue; font-weight: bold;",
        payload
      );
      this.$emit("update-element-property", payload);
    },

    panMap(direction) {
      const panOffset = 50;
      if (this.is3DMode && this.map3DInstance) {
        switch (direction) {
          case "up":
            this.map3DInstance.panBy([0, -panOffset]);
            break;
          case "down":
            this.map3DInstance.panBy([0, panOffset]);
            break;
          case "left":
            this.map3DInstance.panBy([-panOffset, 0]);
            break;
          case "right":
            this.map3DInstance.panBy([panOffset, 0]);
            break;
          case "center":
            if (this.routeBounds) {
              this.map3DInstance.fitBounds(this.routeBounds, {
                padding: 80,
                duration: 500,
              });
            }
            break;
        }
      } else if (this.map2DInstance) {
        switch (direction) {
          case "up":
            this.map2DInstance.panBy([0, -panOffset]);
            break;
          case "down":
            this.map2DInstance.panBy([0, panOffset]);
            break;
          case "left":
            this.map2DInstance.panBy([-panOffset, 0]);
            break;
          case "right":
            this.map2DInstance.panBy([50, 0]);
            break;
          case "center":
            if (this.activityData?.streams?.latlng?.data) {
              this.map2DInstance.fitBounds(
                this.activityData.streams.latlng.data
              );
            }
            break;
        }
      }
    },

    updateCamera3D() {
      if (this.is3DMode && this.map3DInstance && this.routeCenter) {
        this.map3DInstance.easeTo({
          center: this.routeCenter,
          pitch: this.mapSettings.pitch,
          bearing: this.mapSettings.bearing,
          duration: 500,
        });
      }
    },

    zoomIn() {
      const zoomIncrement = 0.2;
      if (this.is3DMode && this.map3DInstance) {
        this.map3DInstance.zoomTo(
          this.map3DInstance.getZoom() + zoomIncrement,
          {
            duration: 200,
          }
        );
      } else if (this.map2DInstance) {
        this.map2DInstance.zoomIn(zoomIncrement);
      }
    },

    zoomOut() {
      const zoomIncrement = 0.2;
      if (this.is3DMode && this.map3DInstance) {
        this.map3DInstance.zoomTo(
          this.map3DInstance.getZoom() - zoomIncrement,
          {
            duration: 200,
          }
        );
      } else if (this.map2DInstance) {
        this.map2DInstance.zoomOut(zoomIncrement);
      }
    },

    getCanvasElement() {
      return this.$refs.tshirtMockup;
    },

    startDrag(event, element) {
      this.activeInteraction = { element, type: "drag" };
      this.setupInteraction(event, element);
    },

    startResize(event, element, direction) {
      this.activeInteraction = { element, type: "resize", direction };
      this.setupInteraction(event, element);
    },

    setupInteraction(event, element) {
      const type = element.id.split("_")[0];
      this.$emit("select-element", type, element);
      this.initialMouse = { x: event.clientX, y: event.clientY };
      this.initialElementState = {
        x: element.x,
        y: element.y,
        width: element.width,
        height: element.height,
      };
    },

    handleInteraction(event) {
      if (!this.activeInteraction.type) return;
      if (this.activeInteraction.type === "drag") this.drag(event);
      else if (this.activeInteraction.type === "resize") this.resize(event);
    },

    stopInteraction() {
      if (this.activeInteraction.element) {
        const el = this.activeInteraction.element;
        this.$emit("update-element-geometry", {
          element: el,
          newGeometry: { x: el.x, y: el.y, width: el.width, height: el.height },
        });
      }
      this.activeInteraction = { element: null, type: null, direction: null };
    },

    drag(event) {
      if (!this.$refs.tshirtMockup) return;
      const canvasRect = this.$refs.tshirtMockup.getBoundingClientRect();
      const el = this.activeInteraction.element;
      const movementX = event.clientX - this.initialMouse.x;
      const movementY = event.clientY - this.initialMouse.y;
      let newX = this.initialElementState.x + movementX;
      let newY = this.initialElementState.y + movementY;
      const minX = -(canvasRect.width / 2) + el.width / 2;
      const maxX = canvasRect.width / 2 - el.width / 2;
      const minY = -(canvasRect.height / 2) + el.height / 2;
      const maxY = canvasRect.height / 2 - el.height / 2;
      el.x = Math.max(minX, Math.min(maxX, newX));
      el.y = Math.max(minY, Math.min(maxY, newY));
    },

    resize(event) {
      const { element, direction } = this.activeInteraction;
      const state = this.initialElementState;
      if (!element || !state) return;
      const moveX = event.clientX - this.initialMouse.x;
      const moveY = event.clientY - this.initialMouse.y;
      let newWidth = state.width;
      let newHeight = state.height;
      let newX = state.x;
      let newY = state.y;
      if (direction.includes("right")) {
        newWidth = state.width + moveX;
        newX = state.x + moveX / 2;
      }
      if (direction.includes("left")) {
        newWidth = state.width - moveX;
        newX = state.x + moveX / 2;
      }
      if (direction.includes("bottom")) {
        newHeight = state.height + moveY;
        newY = state.y + moveY / 2;
      }
      if (direction.includes("top")) {
        newHeight = state.height - moveY;
        newY = state.y + moveY / 2;
      }
      if (newWidth >= this.minSize) {
        element.width = newWidth;
        element.x = newX;
      }
      if (newHeight >= this.minSize) {
        element.height = newHeight;
        element.y = newY;
      }
    },

    initializeMap() {
      if (this.map2DInstance) {
        this.map2DInstance.remove();
        this.map2DInstance = null;
      }
      if (this.map3DInstance) {
        this.map3DInstance.remove();
        this.map3DInstance = null;
      }

      if (this.is3DMode) {
        this.initMap3D();
      } else {
        this.initMap2D();
      }
    },

    initMap2D() {
      if (!this.$refs.mapContainer2D || !this.activityData) return;

      this.map2DInstance = L.map(this.$refs.mapContainer2D, {
        attributionControl: false,
        zoomControl: false,
        dragging: false,
        scrollWheelZoom: false,
        zoomDelta: 0.2,
        zoomSnap: 0.1,
      });

      const plainCoordinates = toRaw(this.activityData.streams.latlng.data);
      this.map2DInstance.fitBounds(plainCoordinates);
      this.updateMapTileLayer();
      this.updateMap();

      this.$nextTick(() => this.map2DInstance.invalidateSize());
      this.$emit("update-map-instance", this.map2DInstance);
    },

    initMap3D() {
      if (!this.$refs.mapContainer3D || !this.activityData) return;
      const styleUrl = TILE_LAYERS[this.mapSettings.style].url;
      const latlngs = this.activityData.streams.latlng.data;
      const bounds = L.latLngBounds(latlngs)
        .toBBoxString()
        .split(",")
        .map(Number);
      this.routeBounds = bounds;
      const center = L.latLngBounds(latlngs).getCenter();
      this.routeCenter = [center.lng, center.lat];
      this.map3DInstance = new maplibregl.Map({
        container: this.$refs.mapContainer3D,
        style: styleUrl,
        interactive: false,
        pitch: this.mapSettings.pitch,
        bearing: this.mapSettings.bearing,
        center: this.routeCenter,
        attributionControl: false,
      });
      this.map3DInstance.on("load", () => {
        const layers = toRaw(this.map3DInstance.getStyle().layers);
        layers.forEach((layer) => {
          if (layer.type === "line" && layer.id !== "route") {
            this.map3DInstance.setPaintProperty(layer.id, "line-opacity", 0.15);
          }
          if (layer.type === "symbol" && layer.id.includes("road")) {
            this.map3DInstance.setLayoutProperty(
              layer.id,
              "visibility",
              "none"
            );
          }
        });
        this.map3DInstance.addSource("route", {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: {
              type: "LineString",
              coordinates: latlngs.map((p) => [p[1], p[0]]),
            },
          },
        });
        this.map3DInstance.addLayer({
          id: "route",
          type: "line",
          source: "route",
          layout: { "line-join": "round", "line-cap": "round" },
          paint: {
            "line-color": String(this.mapSettings.lineColor),
            "line-width": Number(this.mapSettings.lineWeight),
            "line-opacity": 0.9,
          },
        });
        this.map3DInstance.addSource("maptiler-dem", {
          type: "raster-dem",
          url: `https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
        });
        this.map3DInstance.setTerrain({
          source: "maptiler-dem",
          exaggeration: 1.5,
        });
        this.map3DInstance.fitBounds(bounds, { padding: 80, duration: 0 });
        this.map3DInstance.resize();
      });
      this.$emit("update-map-instance", this.map3DInstance);
    },

    updateMapTileLayer() {
      if (!this.map2DInstance) return;
      if (this.currentTileLayer) {
        this.map2DInstance.removeLayer(this.currentTileLayer);
      }
      const styleKey = this.mapSettings.style;
      const layerConfig = TILE_LAYERS[styleKey];
      if (styleKey === "none" || !layerConfig) {
        return;
      }
      this.currentTileLayer = L.tileLayer(layerConfig.url, {
        attribution: layerConfig.attribution,
        tileSize: 512,
        zoomOffset: -1,
      }).addTo(this.map2DInstance);
    },

    updateMap() {
      if (this.is3DMode) {
        if (this.map3DInstance && this.map3DInstance.getLayer("route")) {
          this.map3DInstance.setPaintProperty(
            "route",
            "line-color",
            String(this.mapSettings.lineColor)
          );
          this.map3DInstance.setPaintProperty(
            "route",
            "line-width",
            Number(this.mapSettings.lineWeight)
          );
        }
      } else {
        if (!this.map2DInstance) return;
        this.mapPolylines.forEach((p) => this.map2DInstance.removeLayer(p));
        this.mapPolylines = [];
        this.updateStartEndMarkers();
        if (this.mapSettings.gradientData === "none") {
          this.drawSolidLine();
        } else {
          this.drawGradientLine();
        }
      }
    },

    drawSolidLine() {
      if (!this.activityData?.streams?.latlng?.data) return;
      const latlngs = toRaw(this.activityData.streams.latlng.data);
      const polyline = L.polyline(latlngs, {
        color: this.mapSettings.lineColor,
        weight: this.mapSettings.lineWeight,
        opacity: 0.7,
      }).addTo(this.map2DInstance);
      this.mapPolylines.push(polyline);
    },

    drawGradientLine() {
      if (!this.activityData?.streams) return;
      const streamKey = this.mapSettings.gradientData;
      const latlngs = toRaw(this.activityData.streams.latlng.data);
      const rawData = toRaw(this.activityData.streams[streamKey]?.data);
      const scheme = gradientColorSchemes[streamKey];
      if (!latlngs || !rawData || !scheme || latlngs.length !== rawData.length)
        return;
      const data = this.smoothData(rawData, 40);
      const sortedData = [...data].sort((a, b) => a - b);
      const p5Index = Math.floor(sortedData.length * 0.05);
      const p95Index = Math.ceil(sortedData.length * 0.95) - 1;
      const minVal = sortedData[p5Index];
      const maxVal = sortedData[p95Index];
      for (let i = 0; i < latlngs.length - 1; i++) {
        const value = (data[i] + data[i + 1]) / 2;
        const color = this.getColorForValue(
          value,
          minVal,
          maxVal,
          scheme.min,
          scheme.max
        );
        const segment = L.polyline([latlngs[i], latlngs[i + 1]], {
          color,
          weight: this.mapSettings.lineWeight,
          opacity: 0.85,
        }).addTo(this.map2DInstance);
        this.mapPolylines.push(segment);
      }
    },

    smoothData(data, windowSize) {
      if (windowSize < 1) return [...data];
      const smoothed = [];
      const halfWindow = Math.floor(windowSize / 2);
      for (let i = 0; i < data.length; i++) {
        const start = Math.max(0, i - halfWindow);
        const end = Math.min(data.length - 1, i + halfWindow);
        let sum = 0;
        for (let j = start; j <= end; j++) {
          sum += data[j];
        }
        smoothed.push(sum / (end - start + 1));
      }
      return smoothed;
    },

    getColorForValue(value, min, max, startColor, endColor) {
      let ratio = (value - min) / (max - min);
      ratio = Math.max(0, Math.min(1, ratio));
      if (isNaN(ratio)) {
        ratio = 0.5;
      }
      const start = this.hexToRgb(startColor);
      const end = this.hexToRgb(endColor);
      if (!start || !end) return "#000";
      const r = Math.round(start.r + ratio * (end.r - start.r));
      const g = Math.round(start.g + ratio * (end.g - start.g));
      const b = Math.round(start.b + ratio * (end.b - start.b));
      return `rgb(${r}, ${g}, ${b})`;
    },

    hexToRgb(hex) {
      const bigint = parseInt(hex.slice(1), 16);
      return {
        r: (bigint >> 16) & 255,
        g: (bigint >> 8) & 255,
        b: bigint & 255,
      };
    },

    updateStartEndMarkers() {
      if (this.startEndMarkersInstance) {
        if (this.startEndMarkersInstance.start instanceof L.Marker) {
          this.map2DInstance?.removeLayer(this.startEndMarkersInstance.start);
          this.map2DInstance?.removeLayer(this.startEndMarkersInstance.end);
        } else {
          this.startEndMarkersInstance.start.remove();
          this.startEndMarkersInstance.end.remove();
        }
        this.startEndMarkersInstance = null;
      }
      if (
        !this.mapSettings.showStartEndMarkers ||
        !this.activityData?.streams?.latlng?.data ||
        this.activityData.streams.latlng.data.length < 2
      ) {
        return;
      }

      const latlngs = this.activityData.streams.latlng.data;
      const startPoint = latlngs[0];
      const endPoint = latlngs[latlngs.length - 1];

      if (this.is3DMode && this.map3DInstance) {
        const baseMarkerStyle = {
          width: "14px",
          height: "14px",
          borderRadius: "50%",
          border: "1.5px solid #1a1a1a",
          boxShadow: "0 1px 4px rgba(0, 0, 0, 0.4)",
          boxSizing: "border-box",
        };

        const startEl = document.createElement("div");
        Object.assign(startEl.style, baseMarkerStyle, {
          backgroundColor: "#28a745",
        });

        const endEl = document.createElement("div");
        Object.assign(endEl.style, baseMarkerStyle, {
          backgroundColor: "#fff",
          backgroundImage: `linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000),
                            linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000)`,
          backgroundSize: "8px 8px",
          backgroundPosition: "0 0, 4px 4px",
        });

        const startMarker = new maplibregl.Marker({ element: startEl })
          .setLngLat([startPoint[1], startPoint[0]])
          .addTo(this.map3DInstance);

        const endMarker = new maplibregl.Marker({ element: endEl })
          .setLngLat([endPoint[1], endPoint[0]])
          .addTo(this.map3DInstance);

        this.startEndMarkersInstance = { start: startMarker, end: endMarker };
      } else if (!this.is3DMode && this.map2DInstance) {
        const startDotIcon = L.divIcon({
          className: "start-dot-marker",
          html: "<div></div>",
          iconSize: [14, 14],
          iconAnchor: [7, 7],
        });
        const endDotIcon = L.divIcon({
          className: "end-dot-marker",
          html: "<div></div>",
          iconSize: [14, 14],
          iconAnchor: [7, 7],
        });

        const startMarker = L.marker(startPoint, { icon: startDotIcon });
        const endMarker = L.marker(endPoint, { icon: endDotIcon });

        this.startEndMarkersInstance = { start: startMarker, end: endMarker };
        this.startEndMarkersInstance.start.addTo(this.map2DInstance);
        this.startEndMarkersInstance.end.addTo(this.map2DInstance);
      }
    },

    getGraphElementStyle(graph) {
      return {
        transform: `translate(-50%, -50%) translate(${graph.x}px, ${graph.y}px)`,
        width: `${graph.width}px`,
        height: `${graph.height}px`,
        zIndex: graph.zIndex,
        cursor:
          this.activeInteraction.element?.id === graph.id ? "grabbing" : "grab",
      };
    },

    getTextBoxStyle(box) {
      const style = {
        transform: `translate(-50%, -50%) translate(${box.x}px, ${box.y}px)`,
        width: `${box.width}px`,
        height: `${box.height}px`,
        zIndex: box.zIndex,
        cursor:
          this.activeInteraction.element?.id === box.id ? "grabbing" : "grab",
        backgroundColor: box.transparentBg
          ? "transparent"
          : box.backgroundColor,
      };
      if (!box.transparentBg && box.borderRadius > 0) {
        style.borderRadius = `${box.borderRadius}px`;
        style.overflow = "hidden";
      }
      return style;
    },

    getPhotoElementStyle(photo) {
      const style = {
        transform: `translate(-50%, -50%) translate(${photo.x}px, ${photo.y}px)`,
        width: `${photo.width}px`,
        height: `${photo.height}px`,
        zIndex: photo.zIndex,
        cursor:
          this.activeInteraction.element?.id === photo.id ? "grabbing" : "grab",
      };
      const masks = {
        circle: "circle(50% at 50% 50%)",
        hexagon:
          "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
        arch: 'path("M 0 200 C 0 100, 100 0, 200 0 C 300 0, 400 100, 400 200 Z")',
      };
      if (photo.mask && masks[photo.mask]) style.clipPath = masks[photo.mask];
      return style;
    },

    getQrCodeElementStyle(qrCode) {
      const style = {
        transform: `translate(-50%, -50%) translate(${qrCode.x}px, ${qrCode.y}px)`,
        width: `${qrCode.width}px`,
        height: `${qrCode.height}px`,
        zIndex: qrCode.zIndex,
        cursor:
          this.activeInteraction.element?.id === qrCode.id
            ? "grabbing"
            : "grab",
        borderRadius: `${qrCode.borderRadius}px`,
        overflow: "hidden",
        backgroundColor: qrCode.transparentElementBg
          ? "transparent"
          : qrCode.backgroundColor,
      };

      if (qrCode.borderWidth > 0) {
        style.border = `${qrCode.borderWidth}px solid ${qrCode.borderColor}`;
      }

      return style;
    },

    getQrTextStyle(qrCode) {
      return {
        fontFamily: qrCode.fontFamily,
        fontSize: `${qrCode.fontSize}px`,
        color: qrCode.textColor,
      };
    },

    getCellBorderStyle(index) {
      const { borderStyle, borderColor, columns } = this.dataFields;
      if (borderStyle === "none" || borderStyle === "outer") return {};
      const total = this.selectedDataFields.length;
      if (columns <= 0 || total === 0) return {};
      const styles = {};
      const isLastCol = (index + 1) % columns === 0 || index === total - 1;
      const isLastRow =
        Math.floor(index / columns) === Math.floor((total - 1) / columns);

      if (borderStyle === "inner" || borderStyle === "all") {
        if (!isLastCol) styles.borderRight = `1.5px solid ${borderColor}`;
        if (!isLastRow) styles.borderBottom = `1.5px solid ${borderColor}`;
      } else if (borderStyle === "inner-minimal") {
        const bgImages = [];
        if (!isLastRow)
          bgImages.push(
            `linear-gradient(${borderColor}, ${borderColor}) bottom center / 80% 1.5px no-repeat`
          );
        if (!isLastCol)
          bgImages.push(
            `linear-gradient(${borderColor}, ${borderColor}) right center / 1.5px 80% no-repeat`
          );
        if (bgImages.length > 0) styles.background = bgImages.join(", ");
      }
      return styles;
    },

    getEditableTextStyle(box) {
      return {
        fontFamily: box.fontFamily,
        fontSize: `${box.fontSize}px`,
        color: box.fontColor,
        justifyContent: {
          left: "flex-start",
          center: "center",
          right: "flex-end",
        }[box.textAlign],
        fontWeight: box.isBold ? "bold" : "normal",
        fontStyle: box.isItalic ? "italic" : "normal",
        whiteSpace: "pre-wrap",
        textAlign: box.textAlign,
      };
    },
  },

  beforeUnmount() {
    if (this.map2DInstance) {
      this.map2DInstance.remove();
      this.map2DInstance = null;
    }
    if (this.map3DInstance) {
      this.map3DInstance.remove();
      this.map3DInstance = null;
    }
  },
};
</script>

<style scoped>
.start-dot-marker-3d,
.end-dot-marker-3d {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1.5px solid #1a1a1a;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
  box-sizing: border-box;
}

.start-dot-marker-3d {
  background-color: #28a745;
}

.end-dot-marker-3d {
  background-color: #fff;
  background-image: linear-gradient(
      45deg,
      #000 25%,
      transparent 25%,
      transparent 75%,
      #000 75%,
      #000
    ),
    linear-gradient(
      45deg,
      #000 25%,
      transparent 25%,
      transparent 75%,
      #000 75%,
      #000
    );
  background-size: 8px 8px;
  background-position: 0 0, 4px 4px;
}

.editor-canvas-container {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  overflow: auto;
  background-color: #f0f2f5;
}

.loading-message {
  text-align: center;
  color: #666;
}

.editor-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.tshirt-mockup {
  position: relative;
  width: 600px;
  height: 750px;
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.design-area {
  position: absolute;
  left: 50%;
  top: 50%;
  border: 2px dashed transparent;
  background-color: rgba(255, 255, 255, 0.7);
  cursor: grab;
  will-change: transform, width, height;
}

.design-area.selected {
  border-color: #4287f5;
}

.design-area.is-transparent {
  background-color: transparent !important;
}

.design-area.no-map-bg {
  background-color: transparent !important;
}

.design-area.fade-active {
  background-color: transparent;
}

#map {
  position: relative;
  width: 100%;
  height: 100%;
}

.design-area.no-map-bg #map .leaflet-container {
  background-color: transparent !important;
}

.map-container-base {
  width: 100%;
  height: 100%;
}

.resize-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  background-color: #4287f5;
  border: 1px solid white;
  z-index: 10;
}

.resize-handle.top-left {
  top: -5px;
  left: -5px;
  cursor: nwse-resize;
}

.resize-handle.top {
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  cursor: ns-resize;
}

.resize-handle.top-right {
  top: -5px;
  right: -5px;
  cursor: nesw-resize;
}

.resize-handle.right {
  top: 50%;
  right: -5px;
  transform: translateY(-50%);
  cursor: ew-resize;
}

.resize-handle.bottom-right {
  bottom: -5px;
  right: -5px;
  cursor: nwse-resize;
}

.resize-handle.bottom {
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  cursor: ns-resize;
}

.resize-handle.bottom-left {
  bottom: -5px;
  left: -5px;
  cursor: nesw-resize;
}

.resize-handle.left {
  top: 50%;
  left: -5px;
  transform: translateY(-50%);
  cursor: ew-resize;
}

.data-field-area {
  background-color: transparent !important;
  border: 1.5px solid transparent;
  padding: 0;
}

.data-grid {
  display: grid;
  height: 100%;
  width: 100%;
}

.data-cell {
  background-color: transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 5px;
  text-align: center;
  overflow: hidden;
}

.data-label {
  font-size: 0.8em;
  color: #666;
  white-space: nowrap;
}

.data-value {
  font-size: 1.2em;
  font-weight: bold;
  color: #333;
  white-space: nowrap;
}

.map-legend {
  position: absolute;
  bottom: 10px;
  left: 10px;
  z-index: 1000;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 5px;
  padding: 5px 8px;
  display: flex;
  align-items: center;
  pointer-events: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.legend-gradient {
  width: 40px;
  height: 8px;
  border-radius: 4px;
  margin-right: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.legend-label {
  font-size: 12px;
  color: #333;
  font-weight: 500;
}

.editable-text {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  outline: none;
  line-height: 1.2;
  pointer-events: none;
}

.photo-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  color: #888;
  font-style: italic;
  user-select: none;
}

.badge-list-area {
  padding: 10px 15px;
  box-sizing: border-box;
  border-radius: 10px;
  overflow: hidden;
}

.badge-list-content {
  width: 100%;
  height: 100%;
  overflow-y: hidden;
  text-align: left;
}

.badge-list-item {
  margin: 0 0 4px 0;
  padding: 0;
  line-height: 1.4;
  list-style-type: disc;
  display: list-item;
  margin-left: 1.5em;
}

.qr-code-wrapper {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  height: 100%;
  gap: 15px;
  padding: 5px;
  box-sizing: border-box;
}

.qr-image {
  height: 100%;
  width: auto;
  aspect-ratio: 1 / 1;
  object-fit: contain;
  flex-shrink: 0;
  border-radius: 4px;
}

.qr-text-container {
  display: flex;
  align-items: center;
  flex-grow: 1;
  overflow: hidden;
  height: 100%;
}

.qr-text {
  font-family: "Inter", sans-serif;
  font-weight: bold;
  font-size: 24px;
  color: #333;
  white-space: pre-wrap;
  text-align: left;
}

.qr-text-input {
  width: 100%;
  height: 100%;
  background: transparent;
  border: none;
  outline: none;
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  font-family: "Inter", sans-serif;
  font-weight: bold;
  font-size: 24px;
  color: #333;
  resize: none;
  text-align: left;
}

.weather-area {
}

.weather-content {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  gap: 10px;
  padding: 5px;
  box-sizing: border-box;
}

.weather-icon-emoji {
  font-size: 2.5em;
  line-height: 1;
}

.weather-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  line-height: 1.2;
}

.weather-temp {
  font-weight: bold;
}

.weather-desc {
  font-size: 0.8em;
  opacity: 0.9;
}

:deep(.start-dot-marker div) {
  width: 100%;
  height: 100%;
  background-color: #28a745;
  border-radius: 50%;
  border: 1.5px solid #1a1a1a;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
  box-sizing: border-box;
}

:deep(.end-dot-marker div) {
  width: 100%;
  height: 100%;
  background-color: #fff;
  background-image: linear-gradient(
      45deg,
      #000 25%,
      transparent 25%,
      transparent 75%,
      #000 75%,
      #000
    ),
    linear-gradient(
      45deg,
      #000 25%,
      transparent 25%,
      transparent 75%,
      #000 75%,
      #000
    );
  background-size: 8px 8px;
  background-position: 0 0, 4px 4px;
  border-radius: 50%;
  border: 1.5px solid #1a1a1a;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
  box-sizing: border-box;
}
</style>
