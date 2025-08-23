<template>
  <div class="design-editor-page">
    <div class="editor-sidebar">
      <h2>Design Elements</h2>

      <div
        :class="{ active: selectedElement === 'map' }"
        class="element-box"
        @click="selectElement('map')"
      >
        <p>Map</p>
        <div v-if="selectedElement === 'map'" @click.stop class="map-options">
          <label for="mapStyle">Map Style:</label>
          <select id="mapStyle" v-model="mapStyle">
            <option value="standard">Standard</option>
            <option value="satellite">Satellite</option>
            <option value="none">None</option>
          </select>
          <template v-if="mapStyle === 'standard' || mapStyle === 'satellite'">
            <label for="mapVisuals">Map Visuals:</label>
            <select id="mapVisuals" v-model="mapVisuals">
              <option value="standard">Standard Color</option>
              <option value="grayscale">Grayscale</option>
              <option value="blue">Blue</option>
              <option value="pink">Pink</option>
              <option value="sepia">Sepia</option>
              <option value="vivid">Vivid</option>
            </select>
          </template>
          <label for="gradientData">Color based on:</label>
          <select id="gradientData" v-model="mapGradientData">
            <option
              v-for="opt in availableGradientOptions"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.text }}
            </option>
          </select>
          <template v-if="mapGradientData === 'none'">
            <label for="lineColor">Line Color:</label>
            <input
              type="color"
              id="lineColor"
              v-model="mapLineColor"
              class="color-picker"
            />
          </template>
          <label for="lineWeight">Line Weight:</label>
          <input
            type="range"
            id="lineWeight"
            min="1"
            max="10"
            v-model.number="mapLineWeight"
            class="range-slider"
          />
          <div class="field-option" style="margin-top: 15px">
            <input
              type="checkbox"
              id="showStartEndMarkers"
              v-model="showStartEndMarkers"
            />
            <label for="showStartEndMarkers">Start/End Markers</label>
          </div>
          <div class="zoom-controls">
            <label>Zoom Level:</label>
            <div class="zoom-buttons">
              <button @click="zoomIn" class="zoom-button">+</button>
              <button @click="zoomOut" class="zoom-button">-</button>
            </div>
          </div>
          <div class="fade-option">
            <label for="fadeEdges">Fade Edges:</label>
            <input
              type="checkbox"
              id="fadeEdges"
              v-model="fadeEdges"
              :disabled="mapStyle === 'none'"
            />
          </div>
          <button class="sidebar-button reset-button" @click="resetMap">
            Reset to default
          </button>
          <button class="sidebar-button remove-button" @click="hideMap">
            Delete Map
          </button>
        </div>
      </div>

      <div
        :class="{ active: selectedElement === 'dataFields' }"
        class="element-box"
        @click="selectElement('dataFields')"
      >
        <p>Data Fields</p>
        <div
          v-if="selectedElement === 'dataFields'"
          @click.stop
          class="data-fields-options"
        >
          <div class="option-group">
            <label for="dataColumns">Columns:</label>
            <select id="dataColumns" v-model.number="dataFields.columns">
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            </select>
          </div>
          <div class="option-group">
            <label for="dataBorderStyle">Border Style:</label>
            <select id="dataBorderStyle" v-model="dataFields.borderStyle">
              <option value="inner">Inner Only</option>
              <option value="inner-minimal">Inner Minimal</option>
              <option value="outer">Outer Only</option>
              <option value="all">All Borders</option>
              <option value="none">No Borders</option>
            </select>
          </div>
          <div class="style-group">
            <label>Label Style</label>
            <div class="style-controls">
              <input
                type="color"
                v-model="dataFields.labelColor"
                class="color-picker-small"
              />
              <input
                type="range"
                min="8"
                max="24"
                v-model.number="dataFields.labelSize"
                class="range-slider-small"
              />
            </div>
          </div>
          <div class="style-group">
            <label>Value Style</label>
            <div class="style-controls">
              <input
                type="color"
                v-model="dataFields.valueColor"
                class="color-picker-small"
              />
              <input
                type="range"
                min="10"
                max="48"
                v-model.number="dataFields.valueSize"
                class="range-slider-small"
              />
            </div>
          </div>
          <div class="category-group" @dragleave="clearDropIndicator">
            <p class="category-title">Select & Reorder Fields</p>
            <div
              v-for="field in flatDataFields"
              :key="field.id"
              class="field-option"
              @dragover.prevent="handleDragOver($event, field)"
              @drop="handleDrop($event)"
            >
              <div
                class="drop-indicator"
                :style="{
                  visibility: isDropTarget(field) ? 'visible' : 'hidden',
                }"
              ></div>
              <span
                class="drag-handle"
                draggable="true"
                @dragstart="handleDragStart($event, field)"
                @dragend="handleDragEnd"
                >⠿</span
              >
              <input
                type="checkbox"
                :id="field.id"
                v-model="field.selected"
                @click.stop
              />
              <label :for="field.id">{{ field.label }}</label>
            </div>
            <button
              class="sidebar-button remove-button"
              @click="hideDataFields"
            >
              Delete Data Fields
            </button>
          </div>
        </div>
      </div>

      <div
        :class="{ active: selectedElement === 'graph' }"
        class="element-box"
        @click="handleGraphTileClick"
      >
        <p>Graph</p>
        <div
          v-if="selectedElement === 'graph' && graphElements.length > 0"
          @click.stop
          class="data-fields-options"
        >
          <div v-if="selectedGraph" class="graph-options-panel">
            <div class="option-group">
              <label for="graphData">Data Source:</label>
              <select id="graphData" v-model="selectedGraph.selectedDataSource">
                <option
                  v-for="source in availableGraphSources"
                  :key="source.value"
                  :value="source.value"
                >
                  {{ source.text }}
                </option>
              </select>
            </div>
            <div class="style-group">
              <label>Styling</label>
              <div class="option-group">
                <label for="graphLineColor">Line Color:</label>
                <input
                  type="color"
                  id="graphLineColor"
                  v-model="selectedGraph.lineColor"
                  class="color-picker-small"
                />
              </div>
              <div class="option-group">
                <label>Line Thickness</label>
                <input
                  type="range"
                  v-model.number="selectedGraph.lineThickness"
                  min="1"
                  max="10"
                  class="range-slider"
                />
              </div>
              <div class="option-group">
                <label for="graphFillColor">Fill Color:</label>
                <input
                  type="color"
                  id="graphFillColor"
                  v-model="selectedGraph.fillColor"
                  class="color-picker-small"
                />
              </div>
              <div class="field-option">
                <input
                  type="checkbox"
                  id="transparentFill"
                  v-model="selectedGraph.transparentFill"
                />
                <label for="transparentFill">Transparent Fill</label>
              </div>
              <div class="field-option">
                <input
                  type="checkbox"
                  id="transparentBg"
                  v-model="selectedGraph.transparentBg"
                />
                <label for="transparentBg">Transparent Background</label>
              </div>
            </div>
            <div class="style-group">
              <label>Display Options</label>
              <div class="field-option">
                <input
                  type="checkbox"
                  id="showLegend"
                  v-model="selectedGraph.showLegend"
                />
                <label for="showLegend">Show Title</label>
              </div>
              <div class="field-option">
                <input
                  type="checkbox"
                  id="showGrid"
                  v-model="selectedGraph.showGrid"
                />
                <label for="showGrid">Show Grid</label>
              </div>
              <div
                class="field-option"
                v-if="selectedGraph.selectedDataSource !== 'altitude'"
              >
                <input
                  type="checkbox"
                  id="showAltitudeInBackground"
                  v-model="selectedGraph.showAltitudeInBackground"
                />
                <label for="showAltitudeInBackground"
                  >Show Altitude in Background</label
                >
              </div>
            </div>
            <div class="style-group">
              <label>Axes</label>
              <div class="field-option">
                <input
                  type="checkbox"
                  id="showXAxisTitle"
                  v-model="selectedGraph.showXAxisTitle"
                />
                <label for="showXAxisTitle">Show X-Axis Title</label>
              </div>
              <div class="field-option">
                <input
                  type="checkbox"
                  id="showXAxisLabels"
                  v-model="selectedGraph.showXAxisLabels"
                />
                <label for="showXAxisLabels">Show X-Axis Labels</label>
              </div>
              <div class="field-option">
                <input
                  type="checkbox"
                  id="showYAxisTitle"
                  v-model="selectedGraph.showYAxisTitle"
                />
                <label for="showYAxisTitle">Show Y-Axis Title</label>
              </div>
              <div class="field-option">
                <input
                  type="checkbox"
                  id="showYAxisLabels"
                  v-model="selectedGraph.showYAxisLabels"
                />
                <label for="showYAxisLabels">Show Y-Axis Labels</label>
              </div>
              <div class="option-group">
                <label for="xAxisTicks"
                  >Horizontal Ticks: {{ selectedGraph.xAxisTicks }}</label
                >
                <input
                  type="range"
                  id="xAxisTicks"
                  v-model.number="selectedGraph.xAxisTicks"
                  min="2"
                  max="25"
                  class="range-slider"
                />
              </div>
              <div class="option-group">
                <label for="yAxisTicks"
                  >Vertical Ticks: {{ selectedGraph.yAxisTicks }}</label
                >
                <input
                  type="range"
                  id="yAxisTicks"
                  v-model.number="selectedGraph.yAxisTicks"
                  min="2"
                  max="20"
                  class="range-slider"
                />
              </div>
              <div class="option-group">
                <label for="tickFontSize"
                  >Tick Font Size: {{ selectedGraph.tickFontSize }}</label
                >
                <input
                  type="range"
                  id="tickFontSize"
                  v-model.number="selectedGraph.tickFontSize"
                  min="8"
                  max="20"
                  class="range-slider"
                />
              </div>
            </div>
          </div>
          <button
            v-if="graphElements.length < 3"
            @click="addGraph"
            class="sidebar-button add-button"
          >
            + Add Graph
          </button>
          <button
            class="sidebar-button remove-button"
            @click="removeSelectedGraph"
          >
            Delete Graph
          </button>
        </div>
      </div>

      <div
        :class="{ active: selectedElement === 'textBox' }"
        class="element-box"
        @click="handleTextBoxTileClick"
      >
        <p>Text Box</p>
        <div
          v-if="selectedElement === 'textBox' && selectedTextBox"
          @click.stop
          class="data-fields-options"
        >
          <div class="option-group">
            <label for="textBoxContent">Text Content:</label>
            <textarea
              id="textBoxContent"
              v-model="selectedTextBox.text"
              rows="3"
              style="width: 100%"
            ></textarea>
          </div>
          <div class="style-group">
            <div class="option-group">
              <label for="fontFamily">Font:</label>
              <select id="fontFamily" v-model="selectedTextBox.fontFamily">
                <option value="Arial">Arial</option>
                <option value="Verdana">Verdana</option>
                <option value="Georgia">Georgia</option>
                <option value="Times New Roman">Times New Roman</option>
                <option value="Courier New">Courier New</option>
              </select>
            </div>
            <div class="option-group">
              <label for="fontSize">Size</label>
              <input
                type="range"
                id="fontSize"
                v-model.number="selectedTextBox.fontSize"
                min="12"
                max="120"
                class="range-slider"
              />
            </div>
            <div class="option-group">
              <label for="fontColor">Color:</label>
              <input
                type="color"
                id="fontColor"
                v-model="selectedTextBox.fontColor"
                class="color-picker-small"
              />
            </div>
          </div>
          <div class="style-group">
            <div class="option-group">
              <label>Alignment</label>
              <div class="button-group">
                <button
                  :class="{ active: selectedTextBox.textAlign === 'left' }"
                  @click="selectedTextBox.textAlign = 'left'"
                >
                  Left
                </button>
                <button
                  :class="{ active: selectedTextBox.textAlign === 'center' }"
                  @click="selectedTextBox.textAlign = 'center'"
                >
                  Center
                </button>
                <button
                  :class="{ active: selectedTextBox.textAlign === 'right' }"
                  @click="selectedTextBox.textAlign = 'right'"
                >
                  Right
                </button>
              </div>
            </div>
            <div class="field-option">
              <input
                type="checkbox"
                :id="'bold-' + selectedTextBox.id"
                v-model="selectedTextBox.isBold"
              />
              <label :for="'bold-' + selectedTextBox.id">Bold</label>
            </div>
            <div class="field-option">
              <input
                type="checkbox"
                :id="'italic-' + selectedTextBox.id"
                v-model="selectedTextBox.isItalic"
              />
              <label :for="'italic-' + selectedTextBox.id">Italic</label>
            </div>
          </div>
          <button
            v-if="textBoxes.length < 3"
            @click="addTextBox"
            class="sidebar-button add-button"
          >
            + Add Text Box
          </button>
          <button
            class="sidebar-button remove-button"
            @click="removeSelectedTextBox"
          >
            Delete Text Box
          </button>
        </div>
      </div>

      <div
        :class="{ active: selectedElement === 'photo' }"
        class="element-box"
        @click="handlePhotoTileClick"
      >
        <p>Photo</p>
        <div
          v-if="selectedElement === 'photo' && selectedPhoto"
          @click.stop
          class="data-fields-options"
        >
          <div class="photo-selection-container">
            <p class="category-title">Select from Activity</p>
            <div class="photo-grid">
              <div
                v-for="photo in activityPhotos"
                :key="photo.unique_id"
                class="photo-thumbnail"
                @click="selectActivityPhoto(photo)"
              >
                <img :src="photo.urls['600']" alt="Activity Photo Thumbnail" />
              </div>
              <p v-if="activityPhotos.length === 0" class="no-photos-message">
                No photos found in this activity.
              </p>
            </div>
          </div>
          <div class="style-group">
            <div class="option-group">
              <label for="photoMask">Mask (Shape):</label>
              <select id="photoMask" v-model="selectedPhoto.mask">
                <option value="none">Rectangle</option>
                <option value="circle">Circle</option>
                <option value="hexagon">Hexagon</option>
                <option value="arch">Arch</option>
              </select>
            </div>
            <div class="option-group">
              <label for="photoFilter">Filter:</label>
              <select id="photoFilter" v-model="selectedPhoto.filter">
                <option value="none">None</option>
                <option value="grayscale(100%)">Black & White</option>
                <option value="sepia(100%)">Sepia</option>
                <option value="contrast(150%)">High Contrast</option>
                <option value="saturate(200%)">Vibrant</option>
                <option value="hue-rotate(180deg)">Invert Hue</option>
              </select>
            </div>
          </div>
          <div class="photo-upload-container">
            <p class="category-title">Or Upload a Photo</p>
            <input
              type="file"
              id="photoUpload"
              @change="handlePhotoUpload"
              accept="image/*"
              style="display: none"
            />
            <label for="photoUpload" class="sidebar-button upload-button"
              >Choose File</label
            >
          </div>
          <button
            v-if="photoElements.length < 3"
            @click="addPhotoElement"
            class="sidebar-button add-button"
          >
            + Add Photo
          </button>
          <button
            class="sidebar-button remove-button"
            @click="removeSelectedPhoto"
          >
            Delete Photo
          </button>
        </div>
      </div>

      <div
        v-if="achievements.length > 0"
        :class="{ active: selectedElement === 'badgeList' }"
        class="element-box"
        @click="handleBadgeTileClick"
      >
        <p>Activity Badges</p>

        <div
          v-if="selectedElement === 'badgeList'"
          @click.stop
          class="badge-options"
        >
          <div class="option-group">
            <label for="badgeFontFamily">Font:</label>
            <select id="badgeFontFamily" v-model="badgeListElement.fontFamily">
              <option value="Arial">Arial</option>
              <option value="Verdana">Verdana</option>
              <option value="Georgia">Georgia</option>
              <option value="Times New Roman">Times New Roman</option>
              <option value="Courier New">Courier New</option>
            </select>
          </div>

          <div class="option-group">
            <label>Font Size: {{ badgeListElement.fontSize }}</label>
            <input
              type="range"
              v-model.number="badgeListElement.fontSize"
              min="10"
              max="48"
              class="range-slider"
            />
          </div>

          <div class="option-group">
            <label>Text Color:</label>
            <input
              type="color"
              v-model="badgeListElement.textColor"
              class="color-picker-small"
            />
          </div>

          <div class="field-option" style="margin-top: 15px">
            <input
              type="checkbox"
              id="badgeTransparentBg"
              v-model="badgeListElement.transparentBg"
            />
            <label for="badgeTransparentBg">Transparent Background</label>
          </div>

          <div v-if="!badgeListElement.transparentBg" class="option-group">
            <label>Background Color:</label>
            <input
              type="color"
              v-model="badgeListElement.backgroundColor"
              class="color-picker-small"
            />
          </div>

          <div class="style-group">
            <div class="field-option">
              <input
                type="checkbox"
                id="badgeBorderEnabled"
                v-model="badgeListElement.borderEnabled"
              />
              <label for="badgeBorderEnabled">Enable Border</label>
            </div>
            <template v-if="badgeListElement.borderEnabled">
              <div class="option-group">
                <label>Border Color:</label>
                <input
                  type="color"
                  v-model="badgeListElement.borderColor"
                  class="color-picker-small"
                />
              </div>
              <div class="option-group">
                <label
                  >Border Thickness: {{ badgeListElement.borderWidth }}px</label
                >
                <input
                  type="range"
                  v-model.number="badgeListElement.borderWidth"
                  min="1"
                  max="10"
                  class="range-slider"
                />
              </div>
            </template>
          </div>

          <div class="category-group">
            <p class="category-title">Select & Reorder Badges</p>
            <div class="achievement-list-sidebar">
              <div
                v-for="ach in sortedAchievements"
                :key="ach.id"
                class="field-option"
                @dragover.prevent="handleBadgeDragOver($event, ach)"
                @drop="handleBadgeDrop($event)"
              >
                <div
                  class="drop-indicator"
                  :style="{
                    visibility: isDropTarget(ach) ? 'visible' : 'hidden',
                  }"
                ></div>
                <span
                  class="drag-handle"
                  draggable="true"
                  @dragstart="handleBadgeDragStart($event, ach)"
                  @dragend="handleBadgeDragEnd"
                  >⠿</span
                >
                <input
                  type="checkbox"
                  :id="ach.id"
                  v-model="ach.selected"
                  @click.stop
                />
                <label :for="ach.id">{{ ach.text }}</label>
              </div>
            </div>
          </div>

          <button @click="removeBadgeList" class="sidebar-button remove-button">
            Delete Badge List
          </button>
        </div>
      </div>

      <div
        :class="{ active: selectedElement === 'qrCode' }"
        class="element-box"
        @click="handleQrCodeTileClick"
      >
        <p>QR Code</p>
        <div
          v-if="selectedElement === 'qrCode' && selectedQrCode"
          @click.stop
          class="data-fields-options"
        >
          <div class="option-group">
            <label>Link Destination</label>
            <div class="field-option">
              <input
                type="radio"
                id="qrLinkActivity"
                value="activity"
                v-model="selectedQrCode.linkType"
              />
              <label for="qrLinkActivity">Link to activity</label>
            </div>
            <div class="field-option">
              <input
                type="radio"
                id="qrLinkProfile"
                value="profile"
                v-model="selectedQrCode.linkType"
              />
              <label for="qrLinkProfile">Link to profile</label>
            </div>
            <div class="field-option">
              <input
                type="radio"
                id="qrLinkCustom"
                value="custom"
                v-model="selectedQrCode.linkType"
              />
              <label for="qrLinkCustom">Custom link</label>
            </div>
          </div>

          <div class="option-group" v-if="selectedQrCode.linkType === 'custom'">
            <label for="customQrLink">Custom URL:</label>
            <div class="custom-link-input">
              <input
                type="text"
                id="customQrLink"
                v-model="selectedQrCode.customLinkInput"
                @keyup.enter="updateCustomQrLink"
                placeholder="https://..."
              />
              <button @click="updateCustomQrLink" class="confirm-button">
                ✓
              </button>
            </div>
          </div>

          <div class="field-option" style="margin-top: 15px">
            <input
              type="checkbox"
              id="qrTransparentBg"
              v-model="selectedQrCode.transparentBg"
            />
            <label for="qrTransparentBg">Transparent Background</label>
          </div>
          <div class="field-option" style="margin-top: 15px">
            <input
              type="checkbox"
              id="qrShowText"
              v-model="selectedQrCode.showText"
            />
            <label for="qrShowText">Show text</label>
          </div>

          <div class="option-group" v-if="selectedQrCode.showText">
            <label for="qrText">Text:</label>
            <input
              type="text"
              id="qrText"
              v-model="selectedQrCode.text"
              style="width: 100%"
            />
          </div>

          <button
            class="sidebar-button remove-button"
            @click="removeSelectedQrCode"
          >
            Delete QR Code
          </button>
        </div>
      </div>
      <div
        v-if="weatherData"
        :class="{ active: selectedElement === 'weather' }"
        class="element-box"
        @click="handleWeatherTileClick"
      >
        <p>Weather</p>
        <div
          v-if="selectedElement === 'weather'"
          @click.stop
          class="weather-options"
        >
          <div class="option-group">
            <label>Font Size: {{ weatherElement.fontSize }}</label>
            <input
              type="range"
              v-model.number="weatherElement.fontSize"
              min="12"
              max="48"
              class="range-slider"
            />
          </div>
          <div class="option-group">
            <label>Text Color:</label>
            <input
              type="color"
              v-model="weatherElement.textColor"
              class="color-picker-small"
            />
          </div>
          <div class="field-option">
            <input
              type="checkbox"
              id="weatherShowIcon"
              v-model="weatherElement.showIcon"
            />
            <label for="weatherShowIcon">Show Icon</label>
          </div>
          <div class="field-option">
            <input
              type="checkbox"
              id="weatherTransparentBg"
              v-model="weatherElement.transparentBg"
            />
            <label for="weatherTransparentBg">Transparent Background</label>
          </div>
          <div v-if="!weatherElement.transparentBg" class="option-group">
            <label>Background Color:</label>
            <input
              type="color"
              v-model="weatherElement.backgroundColor"
              class="color-picker-small"
            />
          </div>
          <button @click="hideWeather" class="sidebar-button remove-button">
            Delete Weather
          </button>
        </div>
      </div>
    </div>

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
        <div class="tshirt-mockup" ref="tshirtMockup" @click="deselectAll">
          <div
            v-show="mapElement.visible"
            :class="{
              'design-area': true,
              selected: selectedElement === 'map',
              'no-map-bg': mapStyle === 'none',
              'fade-active': fadeEdges,
            }"
            :style="mapElementStyle"
            @mousedown.prevent="startDrag($event, 'map')"
            @click.stop="selectElement('map')"
          >
            <div
              v-if="mapElement.width > 0 && mapElement.height > 0"
              id="map"
              ref="mapContainer"
              :style="[mapContainerStyle, fadeMaskStyle]"
            ></div>
            <div v-if="mapGradientData !== 'none'" class="map-legend">
              <span class="legend-gradient" :style="legendGradientStyle"></span>
              <span class="legend-label">{{ currentLegendLabel }}</span>
            </div>
            <template v-if="selectedElement === 'map'">
              <div
                v-for="handle in resizeHandles"
                :key="handle"
                :class="`resize-handle ${handle}`"
                @mousedown.stop.prevent="startResize($event, 'map', handle)"
              ></div>
            </template>
          </div>

          <div
            v-if="dataFields.visible"
            :class="{
              'design-area': true,
              'data-field-area': true,
              selected: selectedElement === 'dataFields',
            }"
            :style="[
              dataFieldsStyle,
              containerBorderStyle,
              { zIndex: dataFields.zIndex },
            ]"
            @mousedown.prevent="startDrag($event, 'dataFields')"
            @click.stop="selectElement('dataFields')"
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
            <template v-if="selectedElement === 'dataFields'">
              <div
                v-for="handle in resizeHandles"
                :key="handle"
                :class="`resize-handle ${handle}`"
                @mousedown.stop.prevent="
                  startResize($event, 'dataFields', handle)
                "
              ></div>
            </template>
          </div>

          <div
            v-for="graph in visibleGraphElements"
            :key="graph.id"
            :class="{
              'design-area': true,
              selected: selectedGraph && selectedGraph.id === graph.id,
              'is-transparent': graph.transparentBg,
            }"
            :style="getGraphElementStyle(graph)"
            @mousedown.prevent="startDrag($event, 'graph', graph)"
            @click.stop="selectElement('graph', graph)"
          >
            <GraphComponent
              v-if="activityData"
              :activity-data="activityData"
              :options="graph"
            ></GraphComponent>
            <template v-if="selectedGraph && selectedGraph.id === graph.id">
              <div
                v-for="handle in resizeHandles"
                :key="handle"
                :class="`resize-handle ${handle}`"
                @mousedown.stop.prevent="
                  startResize($event, 'graph', handle, graph)
                "
              ></div>
            </template>
          </div>

          <div
            v-for="box in textBoxes"
            :key="box.id"
            :class="{
              'design-area': true,
              selected: selectedTextBox && selectedTextBox.id === box.id,
            }"
            :style="getTextBoxStyle(box)"
            @mousedown.prevent="startDrag($event, 'textBox', box)"
            @click.stop="selectElement('textBox', box)"
          >
            <div class="editable-text" :style="getEditableTextStyle(box)">
              {{ box.text }}
            </div>
            <template v-if="selectedTextBox && selectedTextBox.id === box.id">
              <div
                v-for="handle in resizeHandles"
                :key="handle"
                :class="`resize-handle ${handle}`"
                @mousedown.stop.prevent="
                  startResize($event, 'textBox', handle, box)
                "
              ></div>
            </template>
          </div>

          <div
            v-for="photo in photoElements"
            :key="photo.id"
            :class="{
              'design-area': true,
              selected: selectedPhoto && selectedPhoto.id === photo.id,
            }"
            :style="getPhotoElementStyle(photo)"
            @mousedown.prevent="startDrag($event, 'photo', photo)"
            @click.stop="selectElement('photo', photo)"
          >
            <div v-if="!photo.src" class="photo-placeholder">
              Select a photo
            </div>
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
            <template v-if="selectedPhoto && selectedPhoto.id === photo.id">
              <div
                v-for="handle in resizeHandles"
                :key="handle"
                :class="`resize-handle ${handle}`"
                @mousedown.stop.prevent="
                  startResize($event, 'photo', handle, photo)
                "
              ></div>
            </template>
          </div>

          <div
            v-if="badgeListElement.visible"
            :class="{
              'design-area': true,
              'badge-list-area': true,
              selected: selectedElement === 'badgeList',
              'is-transparent': badgeListElement.transparentBg,
            }"
            :style="getBadgeListStyle"
            @mousedown.prevent="startDrag($event, 'badgeList')"
            @click.stop="selectElement('badgeList')"
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
            <template v-if="selectedElement === 'badgeList'">
              <div
                v-for="handle in resizeHandles"
                :key="handle"
                :class="`resize-handle ${handle}`"
                @mousedown.stop.prevent="
                  startResize($event, 'badgeList', handle)
                "
              ></div>
            </template>
          </div>

          <div
            v-for="qrCode in qrCodeElements"
            :key="qrCode.id"
            :class="{
              'design-area': true,
              'qr-code-area': true,
              selected: selectedQrCode && selectedQrCode.id === qrCode.id,
              'is-transparent': qrCode.transparentBg,
            }"
            :style="getQrCodeElementStyle(qrCode)"
            @mousedown.prevent="startDrag($event, 'qrCode', qrCode)"
            @click.stop="selectElement('qrCode', qrCode)"
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
                <span class="qr-text">{{ qrCode.text }}</span>
              </div>
            </div>

            <template v-if="selectedQrCode && selectedQrCode.id === qrCode.id">
              <div
                v-for="handle in resizeHandles"
                :key="handle"
                :class="`resize-handle ${handle}`"
                @mousedown.stop.prevent="
                  startResize($event, 'qrCode', handle, qrCode)
                "
              ></div>
            </template>
          </div>
          <div
            v-if="weatherElement.visible"
            :class="{
              'design-area': true,
              'weather-area': true,
              selected: selectedElement === 'weather',
              'is-transparent': weatherElement.transparentBg,
            }"
            :style="getWeatherElementStyle"
            @mousedown.prevent="startDrag($event, 'weather')"
            @click.stop="selectElement('weather')"
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
            <template v-if="selectedElement === 'weather'">
              <div
                v-for="handle in resizeHandles"
                :key="handle"
                :class="`resize-handle ${handle}`"
                @mousedown.stop.prevent="startResize($event, 'weather', handle)"
              ></div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <div class="editor-tools-sidebar">
      <h2>Tools</h2>
      <div class="tools-section">
        <button @click="saveDesign" class="tool-button save-button">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path
              d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"
            />
          </svg>
          Save Design
        </button>
      </div>
      <div class="tools-section">
        <button @click="clearCanvas" class="tool-button clear-all-button">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path
              d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"
            />
          </svg>
          <span>Clear Canvas</span>
        </button>
      </div>
      <div class="tools-section">
        <p class="category-title">History</p>
        <div class="button-grid-tools">
          <button @click="undo" :disabled="!canUndo" class="tool-button">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"
              />
            </svg>
            Undo
          </button>
          <button @click="redo" :disabled="!canRedo" class="tool-button">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M18.4 10.6C16.55 8.99 14.15 8 11.5 8c-4.65 0-8.58 3.03-9.96 7.22L3.9 16c1.05-3.19 4.05-5.5 7.6-5.5 1.96 0 3.73.72 5.12 1.88L13 16h9V7l-3.6 3.6z"
              />
            </svg>
            Redo
          </button>
        </div>
      </div>
      <div v-if="selectedElement" class="tools-section">
        <p class="category-title">Clipboard</p>
        <div class="button-grid-tools">
          <button
            @click="cutElement"
            :disabled="!canCopyCutDelete"
            class="tool-button"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="6" cy="6" r="3"></circle>
              <circle cx="6" cy="18" r="3"></circle>
              <line x1="20" y1="4" x2="8.12" y2="15.88"></line>
              <line x1="14.47" y1="14.48" x2="20" y2="20"></line>
              <line x1="8.12" y1="8.12" x2="12" y2="12"></line>
            </svg>
            Cut
          </button>
          <button
            @click="copyElement"
            :disabled="!canCopyCutDelete"
            class="tool-button"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"
              />
            </svg>
            Copy
          </button>
          <button
            @click="pasteElement"
            :disabled="!canPaste"
            class="tool-button"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M19 2h-4.18C14.4.84 13.3 0 12 0S9.6.84 9.18 2H5c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 18H5V4h2v3h10V4h2v16z"
              />
            </svg>
            Paste
          </button>
        </div>
      </div>
      <div v-if="selectedElement" class="tools-section">
        <p class="category-title">Actions</p>
        <div class="button-grid-tools">
          <button
            @click="deleteSelectedElement"
            :disabled="!canCopyCutDelete"
            class="tool-button"
          >
            Delete
          </button>
          <button @click="deselectAll" class="tool-button">Deselect</button>
        </div>
      </div>
      <div v-if="selectedElement" class="tools-section">
        <p class="category-title">Alignment</p>
        <div class="button-grid-tools align-grid">
          <button
            @click="alignElement('left')"
            class="tool-button"
            title="Align Left"
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <rect x="1" y="1" width="3" height="18"></rect>
              <rect x="6" y="5" width="8" height="4"></rect>
              <rect x="6" y="11" width="12" height="4"></rect>
            </svg>
          </button>
          <button
            @click="alignElement('center-h')"
            class="tool-button"
            title="Align Center Horizontally"
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <rect x="8.5" y="1" width="3" height="18"></rect>
              <rect x="4" y="5" width="12" height="4"></rect>
              <rect x="2" y="11" width="16" height="4"></rect>
            </svg>
          </button>
          <button
            @click="alignElement('right')"
            class="tool-button"
            title="Align Right"
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <rect x="16" y="1" width="3" height="18"></rect>
              <rect x="6" y="5" width="8" height="4"></rect>
              <rect x="2" y="11" width="12" height="4"></rect>
            </svg>
          </button>
          <button
            @click="alignElement('top')"
            class="tool-button"
            title="Align Top"
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <rect x="1" y="1" width="18" height="3"></rect>
              <rect x="7" y="6" width="4" height="8"></rect>
              <rect x="13" y="6" width="4" height="12"></rect>
            </svg>
          </button>
          <button
            @click="alignElement('center-v')"
            class="tool-button"
            title="Align Center Vertically"
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <rect x="1" y="8.5" width="18" height="3"></rect>
              <rect x="5" y="4" width="4" height="12"></rect>
              <rect x="11" y="2" width="4" height="16"></rect>
            </svg>
          </button>
          <button
            @click="alignElement('bottom')"
            class="tool-button"
            title="Align Bottom"
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <rect x="1" y="16" width="18" height="3"></rect>
              <rect x="7" y="6" width="4" height="8"></rect>
              <rect x="13" y="2" width="4" height="12"></rect>
            </svg>
          </button>
        </div>
      </div>

      <div v-if="selectedElement" class="tools-section">
        <p class="category-title">Order</p>
        <div class="button-grid-tools layer-grid">
          <button
            @click="bringForward"
            class="tool-button"
            title="Bring Forward"
          >
            <svg
              version="1.0"
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 354 321"
              preserveAspectRatio="xMidYMid meet"
            >
              <g
                transform="translate(0.000000,321.000000) scale(0.100000,-0.100000)"
                fill="currentColor"
              >
                <path
                  d="M1700 2816 c-25 -7 -104 -79 -289 -262 l-255 -252 0 -51 c0 -39 5 -56 23 -75 26 -27 73 -39 113 -28 17 4 96 75 196 175 137 135 171 165 180 154 9 -10 12 -184 12 -634 -1 -462 2 -627 11 -647 16 -34 68 -66 105 -66 32 1 75 32 93 67 8 16 11 195 11 648 0 510 3 627 14 631 7 3 81 -63 178 -160 119 -117 175 -166 197 -171 101 -22 169 66 121 157 -21 41 -391 418 -464 473 -65 50 -165 66 -246 41z"
                />
                <path
                  d="M1095 1688 c-121 -61 -249 -124 -285 -140 -36 -17 -72 -35 -80 -39 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -52 -21 -192 -96 -207 -111 -43 -44 -54 -105 -28 -166 17 -42 42 -60 155 -116 47 -23 92 -46 100 -51 8 -5 74 -37 145 -70 72 -34 240 -116 375 -182 304 -150 473 -231 526 -253 57 -23 241 -24 290 -1 19 9 51 23 72 32 20 9 44 20 52 25 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 31 13 207 99 590 289 372 184 398 198 423 237 45 69 30 141 -39 194 -34 26 -166 94 -274 141 -19 8 -42 19 -50 24 -8 5 -21 11 -27 14 -7 3 -19 7 -25 10 -7 3 -21 9 -30 15 -34 19 -53 29 -98 50 -25 12 -52 26 -60 31 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -59 27 -114 55 -54 27 -102 46 -107 43 -5 -3 -9 -56 -9 -119 l0 -113 198 -97 c108 -54 204 -101 212 -106 8 -5 22 -12 30 -15 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 120 -50 128 -69 43 -110 -66 -30 -798 -390 -886 -435 -32 -16 -85 -36 -118 -43 -51 -12 -66 -12 -111 1 -29 8 -60 19 -68 24 -8 5 -22 12 -30 15 -8 3 -22 9 -30 14 -8 5 -35 19 -60 30 -25 12 -52 26 -60 31 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -21 11 -27 14 -7 3 -19 7 -25 10 -7 3 -20 9 -28 14 -8 5 -76 38 -150 74 -408 196 -510 250 -510 267 0 18 20 29 250 137 52 24 102 49 110 54 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 15 6 119 55 178 83 l33 16 -3 119 c-2 69 -7 120 -13 121 -5 1 -109 -47 -230 -107z"
                />
              </g>
            </svg>
            Forward
          </button>
          <button
            @click="sendBackward"
            class="tool-button"
            title="Send Backward"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 354 321"
              preserveAspectRatio="xMidYMid meet"
            >
              <g transform="rotate(180, 177, 160.5)">
                <g
                  transform="translate(0.000000,321.000000) scale(0.100000,-0.100000)"
                  fill="currentColor"
                >
                  <path
                    d="M1700 2816 c-25 -7 -104 -79 -289 -262 l-255 -252 0 -51 c0 -39 5 -56 23 -75 26 -27 73 -39 113 -28 17 4 96 75 196 175 137 135 171 165 180 154 9 -10 12 -184 12 -634 -1 -462 2 -627 11 -647 16 -34 68 -66 105 -66 32 1 75 32 93 67 8 16 11 195 11 648 0 510 3 627 14 631 7 3 81 -63 178 -160 119 -117 175 -166 197 -171 101 -22 169 66 121 157 -21 41 -391 418 -464 473 -65 50 -165 66 -246 41z"
                  />
                  <path
                    d="M1095 1688 c-121 -61 -249 -124 -285 -140 -36 -17 -72 -35 -80 -39 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -52 -21 -192 -96 -207 -111 -43 -44 -54 -105 -28 -166 17 -42 42 -60 155 -116 47 -23 92 -46 100 -51 8 -5 74 -37 145 -70 72 -34 240 -116 375 -182 304 -150 473 -231 526 -253 57 -23 241 -24 290 -1 19 9 51 23 72 32 20 9 44 20 52 25 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 31 13 207 99 590 289 372 184 398 198 423 237 45 69 30 141 -39 194 -34 26 -166 94 -274 141 -19 8 -42 19 -50 24 -8 5 -21 11 -27 14 -7 3 -19 7 -25 10 -7 3 -21 9 -30 15 -34 19 -53 29 -98 50 -25 12 -52 26 -60 31 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -59 27 -114 55 -54 27 -102 46 -107 43 -5 -3 -9 -56 -9 -119 l0 -113 198 -97 c108 -54 204 -101 212 -106 8 -5 22 -12 30 -15 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 120 -50 128 -69 43 -110 -66 -30 -798 -390 -886 -435 -32 -16 -85 -36 -118 -43 -51 -12 -66 -12 -111 1 -29 8 -60 19 -68 24 -8 5 -22 12 -30 15 -8 3 -22 9 -30 14 -8 5 -35 19 -60 30 -25 12 -52 26 -60 31 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -21 11 -27 14 -7 3 -19 7 -25 10 -7 3 -20 9 -28 14 -8 5 -76 38 -150 74 -408 196 -510 250 -510 267 0 18 20 29 250 137 52 24 102 49 110 54 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 15 6 119 55 178 83 l33 16 -3 119 c-2 69 -7 120 -13 121 -5 1 -109 -47 -230 -107z"
                  />
                </g>
              </g>
            </svg>
            Backward
          </button>
          <button
            @click="bringToFront"
            class="tool-button"
            title="Bring to Front"
          >
            <svg
              version="1.0"
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 402 390"
              preserveAspectRatio="xMidYMid meet"
            >
              <g
                transform="translate(0.000000,390.000000) scale(0.100000,-0.100000)"
                fill="currentColor"
              >
                <path
                  d="M1890 3507 c-41 -10 -70 -36 -300 -264 l-255 -252 2 -52 c2 -72 32 -103 103 -103 l51 0 175 175 c139 139 176 171 184 159 6 -9 10 -283 10 -706 0 -756 -1 -738 59 -775 40 -24 68 -24 105 0 57 38 55 9 56 769 0 600 2 703 14 708 9 4 68 -48 163 -144 81 -82 167 -160 190 -171 74 -39 143 -8 157 70 4 20 2 48 -4 63 -10 27 -408 432 -470 478 -70 53 -145 67 -240 45z"
                />
                <path
                  d="M2424 2477 c-2 -7 -3 -62 -2 -121 l3 -108 65 -33 c36 -18 117 -57 180 -88 63 -31 175 -85 248 -121 74 -36 140 -66 147 -66 16 0 26 -25 19 -45 -4 -8 -14 -15 -23 -15 -10 0 -26 -7 -37 -15 -10 -8 -26 -15 -35 -15 -9 0 -22 -7 -29 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -19 -15 -26 -15 -7 0 -159 -72 -336 -161 -178 -88 -351 -169 -385 -180 -62 -20 -64 -20 -125 0 -35 10 -263 118 -507 240 -244 122 -450 221 -456 221 -7 0 -18 6 -25 14 -6 8 -21 16 -33 18 -33 5 -30 49 3 59 14 4 161 75 328 158 l302 151 0 115 c0 114 0 115 -24 115 -13 0 -29 -7 -36 -15 -7 -8 -19 -15 -27 -15 -24 0 -867 -424 -885 -445 -32 -39 -42 -89 -27 -141 15 -51 43 -77 119 -112 105 -48 144 -67 188 -92 9 -6 24 -13 32 -16 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 8 -3 205 -100 436 -215 232 -115 429 -209 438 -209 9 0 28 -7 41 -16 38 -25 203 -22 282 5 49 16 853 406 913 442 8 5 22 12 30 15 8 3 56 25 105 50 50 24 95 44 101 44 7 0 17 7 24 15 7 8 20 15 30 15 26 0 85 65 100 110 16 47 1 106 -34 139 -18 17 -937 481 -952 481 -3 0 -7 -6 -10 -13z"
                />
                <path
                  d="M2976 1341 c-60 -31 -111 -62 -113 -68 -2 -5 48 -36 112 -67 65 -32 115 -63 113 -69 -2 -7 -139 -79 -304 -161 -164 -81 -306 -152 -314 -157 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -23 -9 -203 -95 -220 -105 -38 -23 -119 -39 -147 -28 -14 5 -35 9 -48 9 -20 0 -54 13 -105 42 -8 4 -22 11 -30 14 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -20 8 -197 94 -520 252 -146 72 -272 137 -279 146 -11 13 -8 17 21 29 112 48 206 100 202 110 -5 14 -207 117 -229 117 -21 0 -229 -104 -270 -136 -59 -45 -79 -110 -53 -171 26 -60 36 -66 413 -248 99 -48 239 -115 310 -150 72 -35 150 -73 175 -85 25 -11 52 -25 60 -30 8 -5 35 -18 60 -30 25 -11 52 -25 60 -29 34 -19 197 -96 230 -109 19 -7 70 -16 112 -19 96 -7 144 6 318 89 69 33 168 80 220 105 52 25 102 49 110 54 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 61 24 629 310 646 325 51 48 55 143 7 199 -22 27 -264 161 -298 166 -5 1 -59 -24 -119 -55z"
                />
              </g>
            </svg>
            To Front
          </button>
          <button @click="sendToBack" class="tool-button" title="Send to Back">
            <svg
              width="24"
              height="24"
              viewBox="0 0 402 390"
              preserveAspectRatio="xMidYMid meet"
            >
              <g transform="rotate(180, 201, 195)">
                <g
                  transform="translate(0.000000,390.000000) scale(0.100000,-0.100000)"
                  fill="currentColor"
                >
                  <path
                    d="M1890 3507 c-41 -10 -70 -36 -300 -264 l-255 -252 2 -52 c2 -72 32 -103 103 -103 l51 0 175 175 c139 139 176 171 184 159 6 -9 10 -283 10 -706 0 -756 -1 -738 59 -775 40 -24 68 -24 105 0 57 38 55 9 56 769 0 600 2 703 14 708 9 4 68 -48 163 -144 81 -82 167 -160 190 -171 74 -39 143 -8 157 70 4 20 2 48 -4 63 -10 27 -408 432 -470 478 -70 53 -145 67 -240 45z"
                  />
                  <path
                    d="M2424 2477 c-2 -7 -3 -62 -2 -121 l3 -108 65 -33 c36 -18 117 -57 180 -88 63 -31 175 -85 248 -121 74 -36 140 -66 147 -66 16 0 26 -25 19 -45 -4 -8 -14 -15 -23 -15 -10 0 -26 -7 -37 -15 -10 -8 -26 -15 -35 -15 -9 0 -22 -7 -29 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -19 -15 -26 -15 -7 0 -159 -72 -336 -161 -178 -88 -351 -169 -385 -180 -62 -20 -64 -20 -125 0 -35 10 -263 118 -507 240 -244 122 -450 221 -456 221 -7 0 -18 6 -25 14 -6 8 -21 16 -33 18 -33 5 -30 49 3 59 14 4 161 75 328 158 l302 151 0 115 c0 114 0 115 -24 115 -13 0 -29 -7 -36 -15 -7 -8 -19 -15 -27 -15 -24 0 -867 -424 -885 -445 -32 -39 -42 -89 -27 -141 15 -51 43 -77 119 -112 105 -48 144 -67 188 -92 9 -6 24 -13 32 -16 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 8 -3 205 -100 436 -215 232 -115 429 -209 438 -209 9 0 28 -7 41 -16 38 -25 203 -22 282 5 49 16 853 406 913 442 8 5 22 12 30 15 8 3 56 25 105 50 50 24 95 44 101 44 7 0 17 7 24 15 7 8 20 15 30 15 26 0 85 65 100 110 16 47 1 106 -34 139 -18 17 -937 481 -952 481 -3 0 -7 -6 -10 -13z"
                  />
                  <path
                    d="M2976 1341 c-60 -31 -111 -62 -113 -68 -2 -5 48 -36 112 -67 65 -32 115 -63 113 -69 -2 -7 -139 -79 -304 -161 -164 -81 -306 -152 -314 -157 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -23 -9 -203 -95 -220 -105 -38 -23 -119 -39 -147 -28 -14 5 -35 9 -48 9 -20 0 -54 13 -105 42 -8 4 -22 11 -30 14 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -20 8 -197 94 -520 252 -146 72 -272 137 -279 146 -11 13 -8 17 21 29 112 48 206 100 202 110 -5 14 -207 117 -229 117 -21 0 -229 -104 -270 -136 -59 -45 -79 -110 -53 -171 26 -60 36 -66 413 -248 99 -48 239 -115 310 -150 72 -35 150 -73 175 -85 25 -11 52 -25 60 -30 8 -5 35 -18 60 -30 25 -11 52 -25 60 -29 34 -19 197 -96 230 -109 19 -7 70 -16 112 -19 96 -7 144 6 318 89 69 33 168 80 220 105 52 25 102 49 110 54 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 61 24 629 310 646 325 51 48 55 143 7 199 -22 27 -264 161 -298 166 -5 1 -59 -24 -119 -55z"
                  />
                </g>
              </g>
            </svg>
            To Back
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import GraphComponent from "@/components/GraphComponent.vue";
import QRCode from "qrcode";
import { auth } from "../auth";

const gradientColorSchemes = {
  velocity_smooth: { label: "Speed", min: "#a3d5ff", max: "#003b80" },
  heartrate: { label: "Heart Rate", min: "#ffc4c4", max: "#7a0000" },
  altitude: { label: "Altitude", min: "#d8c3a5", max: "#4a3728" },
  distance: { label: "Time", min: "#ffe3b3", max: "#e67300" },
  watts: { label: "Power", min: "#e6c6ff", max: "#4b0082" },
};

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
    GraphComponent,
  },
  data() {
    return {
      startEndMarkers: null,
      showStartEndMarkers: false,
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
        backgroundColor: "rgba(255, 255, 255, 0.7)",
        transparentBg: false,
      },
      achievements: [],
      draggedBadge: null,
      dropTargetBadge: null,
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
        backgroundColor: "rgba(255, 255, 255, 0.8)",
        transparentBg: false,
        fontFamily: "Arial",
        borderEnabled: false,
        borderColor: "#333333",
        borderWidth: 2,
      },
      zIndexCounter: 3,
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
        width: 540,
        height: 525,
        zIndex: 1,
      },
      mapPolylines: [],
      mapLineColor: "#ff0000",
      mapLineWeight: 3,
      mapGradientData: "none",
      mapStyle: "standard",
      currentTileLayer: null,
      mapVisuals: "standard",
      fadeEdges: false,
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
      },
      graphElements: [],
      selectedGraphIndex: null,
      availableDataFields: [
        {
          name: "General",
          fields: [
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
          ],
        },
        {
          name: "Elevation",
          fields: [
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
          ],
        },
        {
          name: "Pacing",
          fields: [
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
          ],
        },
        {
          name: "Speed",
          fields: [
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
          ],
        },
        {
          name: "Heart Rate",
          fields: [
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
          ],
        },
        {
          name: "Cadence",
          fields: [
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
          ],
        },
        {
          name: "Power",
          fields: [
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
      ],
      textBoxes: [],
      selectedTextBoxIndex: null,
      photoElements: [],
      selectedPhotoIndex: null,
      qrCodeElements: [],
      selectedQrCodeIndex: null,
      selectedElement: "map",
      draggedField: null,
      dropTargetField: null,
      activeInteraction: {
        target: null,
        type: null,
        direction: null,
        index: null,
      },
      initialMouseX: 0,
      initialMouseY: 0,
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
    getWeatherElementStyle() {
      const el = this.weatherElement;
      const style = {
        transform: `translate(-50%, -50%) translate(${el.x}px, ${el.y}px)`,
        width: `${el.width}px`,
        height: `${el.height}px`,
        zIndex: el.zIndex,
        color: el.textColor,
        fontSize: `${el.fontSize}px`,
        backgroundColor: el.transparentBg ? "transparent" : el.backgroundColor,
        cursor:
          this.activeInteraction.type === "drag" &&
          this.activeInteraction.target === "weather"
            ? "grabbing"
            : "grab",
      };
      return style;
    },
    sortedAchievements() {
      return [...this.achievements].sort((a, b) => a.order - b.order);
    },
    visibleBadges() {
      return this.achievements
        .filter((a) => a.selected)
        .sort((a, b) => a.order - b.order);
    },

    getBadgeListStyle() {
      const el = this.badgeListElement;
      const style = {
        transform: `translate(-50%, -50%) translate(${el.x}px, ${el.y}px)`,
        width: `${el.width}px`,
        height: `${el.height}px`,
        color: el.textColor,
        fontSize: `${el.fontSize}px`,
        fontFamily: el.fontFamily, // Toegevoegd
        backgroundColor: el.transparentBg ? "transparent" : el.backgroundColor,
        zIndex: el.zIndex,
        cursor:
          this.activeInteraction.type === "drag" &&
          this.activeInteraction.target === "badgeList"
            ? "grabbing"
            : "grab",
      };
      if (el.borderEnabled) {
        style.border = `${el.borderWidth}px solid ${el.borderColor}`;
      } else {
        style.borderStyle =
          this.selectedElement === "badgeList" ? "dashed" : "solid";
        style.borderColor =
          this.selectedElement === "badgeList" ? "#4287f5" : "transparent";
        style.borderWidth = this.selectedElement === "badgeList" ? "2px" : "0";
      }
      return style;
    },

    canUndo() {
      return this.historyIndex > 0;
    },

    canRedo() {
      return this.historyIndex < this.history.length - 1;
    },

    canCopyCutDelete() {
      return !!this.selectedElement;
    },

    canPaste() {
      return !!this.clipboard;
    },

    designState() {
      return {
        mapSettings: {
          style: this.mapStyle,
          lineColor: this.mapLineColor,
          lineWeight: this.mapLineWeight,
          gradientData: this.mapGradientData,
          visuals: this.mapVisuals,
          fadeEdges: this.fadeEdges,
        },
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

    activeElementObject() {
      if (!this.selectedElement) return null;
      switch (this.selectedElement) {
        case "map":
          return this.mapElement;
        case "dataFields":
          return this.dataFields;
        case "graph":
          return this.selectedGraph;
        case "textBox":
          return this.selectedTextBox;
        case "photo":
          return this.selectedPhoto;
        case "badgeList":
          return this.badgeListElement;
        case "qrCode":
          return this.selectedQrCode;
        case "weather":
          return this.weatherElement;
        default:
          return null;
      }
    },

    selectedTextBox() {
      if (
        this.selectedElement === "textBox" &&
        this.selectedTextBoxIndex !== null &&
        this.textBoxes[this.selectedTextBoxIndex]
      ) {
        return this.textBoxes[this.selectedTextBoxIndex];
      }
      return null;
    },

    selectedPhoto() {
      if (
        this.selectedElement === "photo" &&
        this.selectedPhotoIndex !== null &&
        this.photoElements[this.selectedPhotoIndex]
      ) {
        return this.photoElements[this.selectedPhotoIndex];
      }
      return null;
    },

    selectedQrCode() {
      if (
        this.selectedElement === "qrCode" &&
        this.selectedQrCodeIndex !== null &&
        this.qrCodeElements[this.selectedQrCodeIndex]
      ) {
        return this.qrCodeElements[this.selectedQrCodeIndex];
      }
      return null;
    },

    availableGradientOptions() {
      if (!this.activityData || !this.activityData.streams) return [];
      const allOptions = [
        { value: "none", text: "Solid Color" },
        { value: "velocity_smooth", text: "Speed" },
        { value: "heartrate", text: "Heart Rate" },
        { value: "altitude", text: "Altitude" },
        { value: "distance", text: "Time" },
        { value: "watts", text: "Power" },
      ];
      return allOptions.filter(
        (opt) => opt.value === "none" || this.activityData.streams[opt.value]
      );
    },

    legendGradientStyle() {
      if (this.mapGradientData === "none") return {};
      const scheme = gradientColorSchemes[this.mapGradientData];
      if (!scheme) return {};
      return {
        background: `linear-gradient(to right, ${scheme.min}, ${scheme.max})`,
      };
    },

    currentLegendLabel() {
      if (this.mapGradientData === "none") return "";
      const scheme = gradientColorSchemes[this.mapGradientData];
      return scheme ? scheme.label : "";
    },

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
      return Object.keys(this.activityData.streams)
        .filter((key) => streamLabels[key])
        .map((key) => ({
          value: key,
          text: streamLabels[key],
          yAxisTitle: streamLabels[key],
        }));
    },

    selectedGraph() {
      if (
        this.selectedElement === "graph" &&
        this.selectedGraphIndex !== null &&
        this.graphElements[this.selectedGraphIndex]
      ) {
        return this.graphElements[this.selectedGraphIndex];
      }
      return null;
    },

    visibleGraphElements() {
      return this.graphElements.filter((graph) => graph.visible);
    },

    mapContainerStyle() {
      let style = { width: "100%", height: "100%" };
      if (this.mapStyle === "none") {
        style.backgroundColor = "transparent";
        return style;
      }
      let filter = "";
      if (this.mapVisuals === "grayscale") filter = "grayscale(100%)";
      else if (this.mapVisuals === "blue")
        filter = "sepia(100%) hue-rotate(180deg)";
      else if (this.mapVisuals === "pink")
        filter = "sepia(50%) hue-rotate(300deg) saturate(150%)";
      else if (this.mapVisuals === "sepia") filter = "sepia(100%)";
      else if (this.mapVisuals === "vivid") filter = "saturate(200%)";
      style.filter = filter;
      return style;
    },

    fadeMaskStyle() {
      if (!this.fadeEdges) return {};
      const fadeStart = 0,
        fadeEnd = 100,
        transition = 10;
      const maskImage =
        `linear-gradient(to right, transparent ${fadeStart}%, black ${
          fadeStart + transition
        }%, black ${fadeEnd - transition}%, transparent ${fadeEnd}%), ` +
        `linear-gradient(to bottom, transparent ${fadeStart}%, black ${
          fadeStart + transition
        }%, black ${fadeEnd - transition}%, transparent ${fadeEnd}%)`;
      return {
        maskImage,
        WebkitMaskImage: maskImage,
        maskComposite: "intersect",
        WebkitMaskComposite: "source-in",
      };
    },

    mapElementStyle() {
      return {
        transform: `translate(-50%, -50%) translate(${this.mapElement.x}px, ${this.mapElement.y}px)`,
        cursor:
          this.activeInteraction.type === "drag" &&
          this.activeInteraction.target === "map"
            ? "grabbing"
            : "grab",
        width: `${this.mapElement.width}px`,
        height: `${this.mapElement.height}px`,
        zIndex: this.mapElement.zIndex,
      };
    },

    dataFieldsStyle() {
      return {
        transform: `translate(-50%, -50%) translate(${this.dataFields.x}px, ${this.dataFields.y}px)`,
        cursor:
          this.activeInteraction.type === "drag" &&
          this.activeInteraction.target === "dataFields"
            ? "grabbing"
            : "grab",
        width: `${this.dataFields.width}px`,
        height: `${this.dataFields.height}px`,
      };
    },

    dataGridStyle() {
      return { gridTemplateColumns: `repeat(${this.dataFields.columns}, 1fr)` };
    },

    flatDataFields() {
      return this.availableDataFields
        .flatMap((cat) => cat.fields)
        .sort((a, b) => a.order - b.order);
    },

    selectedDataFields() {
      return this.flatDataFields.filter((field) => field.selected);
    },

    containerBorderStyle() {
      const style = this.dataFields.borderStyle;
      const color = this.dataFields.borderColor;
      const styles = {};
      if (style === "outer" || style === "all") {
        styles.border = `1.5px solid ${color}`;
      }
      return styles;
    },
  },

  watch: {
    showStartEndMarkers() {
      if (this.map) {
        this.updateStartEndMarkers();
      }
    },

    designState: {
      handler(newState) {
        if (this.isApplyingState) {
          return;
        }
        if (this.historyIndex < this.history.length - 1) {
          this.history.splice(this.historyIndex + 1);
        }
        this.history.push(newState);
        this.historyIndex = this.history.length - 1;
        localStorage.setItem("autosavedDesign", JSON.stringify(newState));
      },
      deep: true,
    },

    loading(isLoading) {
      if (!isLoading && this.activityData) {
        this.$nextTick(() => {
          if (!this.map && this.activityData.streams?.latlng) {
            this.initMap();
          }
        });
      }
    },

    activityData(newData) {
      if (newData) {
        this.updateDataFields();
        this.analyzeAchievements();
        this.fetchWeather();
      }
    },

    mapLineColor() {
      if (this.map) this.updateMap();
    },

    mapLineWeight() {
      if (this.map) this.updateMap();
    },

    mapGradientData() {
      if (this.map) this.updateMap();
    },

    mapStyle(newStyle) {
      if (this.map) this.updateMapTileLayer();
      if (newStyle === "none") {
        this.fadeEdges = false;
      }
    },

    mapVisuals() {
      if (this.map) this.updateMapTileLayer();
    },

    "selectedGraph.selectedDataSource"(newSourceKey) {
      if (!this.selectedGraph || !newSourceKey) return;
      const source = this.availableGraphSources.find(
        (s) => s.value === newSourceKey
      );
      if (source) {
        this.selectedGraph.yAxisTitle = source.yAxisTitle;
      }
    },

    "selectedQrCode.linkType"(newVal) {
      if (!this.selectedQrCode) return;
      this.updateQrCodeValue(this.selectedQrCode);
      switch (newVal) {
        case "activity":
          this.selectedQrCode.text = "Give me Kudos!";
          break;
        case "profile":
          this.selectedQrCode.text = "Follow me!";
          break;
        case "custom":
          this.selectedQrCode.text = "Scan Me!";
          break;
      }
    },

    "selectedQrCode.transparentBg"() {
      if (this.selectedQrCode) {
        this.updateQrCodeValue(this.selectedQrCode);
      }
    },
  },

  methods: {
    async saveDesign() {
      // 1. Check if the user is logged in
      if (!auth.isLoggedIn) {
        alert("Please log in or create an account to save your design.");

        // 2. Save the current design to localStorage so we don't lose it
        localStorage.setItem(
          "unsavedGpxDesign",
          JSON.stringify(this.designState)
        );

        // 3. Redirect to the login page with instructions to return here
        this.$router.push({
          name: "Login",
          query: {
            // Tell the login page where to redirect back to
            redirect: this.$route.fullPath,
            // Tell the design page to trigger a save upon return
            action: "save",
          },
        });
        return; // Stop the function here
      }

      // If we reach here, the user is logged in, and we can save normally.
      const designDataToSave = this.designState;

      try {
        const payload = {
          product_id: parseInt(this.productId),
          design_data: designDataToSave,
          name: `Design for ${this.activityData.details.name}`,
        };

        await axios.post("http://localhost:5000/api/designs", payload, {
          withCredentials: true,
        });

        alert("Design saved successfully!");
        localStorage.removeItem("unsavedGpxDesign"); // Clean up temp data
      } catch (error) {
        console.error("Error saving design:", error);
        alert("Failed to save design. Please try again.");
      }
    },

    updateStartEndMarkers() {
      if (this.startEndMarkers) {
        this.map.removeLayer(this.startEndMarkers.start);
        this.map.removeLayer(this.startEndMarkers.end);
        this.startEndMarkers = null;
      }
      if (
        !this.showStartEndMarkers ||
        !this.activityData?.streams?.latlng?.data
      ) {
        return;
      }
      const latlngs = this.activityData.streams.latlng.data;
      if (latlngs.length < 2) return;
      const startPoint = latlngs[0];
      const endPoint = latlngs[latlngs.length - 1];
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
      this.startEndMarkers = { start: startMarker, end: endMarker };
      this.startEndMarkers.start.addTo(this.map);
      this.startEndMarkers.end.addTo(this.map);
    },

    async fetchWeather() {
      if (!this.activityData?.details?.start_latlng?.length) {
        console.log("Geen startlocatie gevonden voor weerdata.");
        return;
      }
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
        const weatherCode = hourlyData.weathercode[closestHourIndex];
        const interpretation = this.getWeatherInterpretation(weatherCode);
        this.weatherData = {
          temp: Math.round(hourlyData.temperature_2m[closestHourIndex]),
          description: interpretation.description,
          icon: interpretation.icon,
        };
        console.log("Weerdata succesvol opgehaald:", this.weatherData);
      } catch (error) {
        console.error(
          "Fout bij het ophalen van weerdata via Open-Meteo:",
          error
        );
        this.weatherData = null;
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
        55: { description: "Dense drizzle", icon: "🌧️" },
        61: { description: "Slight rain", icon: "🌦️" },
        63: { description: "Moderate rain", icon: "🌧️" },
        65: { description: "Heavy rain", icon: " torrential rain" },
        80: { description: "Slight rain showers", icon: "🌦️" },
        81: { description: "Moderate rain showers", icon: "🌧️" },
        82: { description: "Violent rain showers", icon: " torrential rain" },
        95: { description: "Thunderstorm", icon: "⛈️" },
      };
      return codes[code] || { description: "Unknown", icon: "🤷" };
    },

    handleWeatherTileClick() {
      this.weatherElement.visible = true;
      this.selectElement("weather");
    },

    hideWeather() {
      this.weatherElement.visible = false;
      this.deselectAll();
    },

    handleBadgeDragStart(event, badge) {
      this.draggedBadge = badge;
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", badge.id);
    },

    handleBadgeDragOver(event, targetBadge) {
      if (!this.draggedBadge || this.draggedBadge.id === targetBadge.id) return;
      this.dropTargetBadge = targetBadge;
    },

    handleBadgeDrop() {
      if (!this.draggedBadge || !this.dropTargetBadge) return;
      const achievements = [...this.achievements];
      const draggedIndex = achievements.findIndex(
        (a) => a.id === this.draggedBadge.id
      );
      const targetIndex = achievements.findIndex(
        (a) => a.id === this.dropTargetBadge.id
      );
      if (draggedIndex === -1 || targetIndex === -1) return;
      const [draggedItem] = achievements.splice(draggedIndex, 1);
      achievements.splice(targetIndex, 0, draggedItem);
      achievements.forEach((ach, index) => {
        ach.order = index;
      });
      this.achievements = achievements;
      this.handleBadgeDragEnd();
    },

    handleBadgeDragEnd() {
      this.draggedBadge = null;
      this.dropTargetBadge = null;
    },

    getOrdinal(n) {
      const s = ["th", "st", "nd", "rd"];
      const v = n % 100;
      return n + (s[(v - 20) % 10] || s[v] || s[0]);
    },

    analyzeAchievements() {
      if (!this.activityData || !this.activityData.details) return;
      const details = this.activityData.details;
      const efforts = details.segment_efforts || [];
      const bestEfforts = details.best_efforts || [];
      let options = [];
      const getPriority = (type) => {
        switch (type) {
          case "kom":
          case "qom":
            return 1;
          case "top10":
            return 2;
          case "pr":
            return 3;
          case "best_effort_top3":
            return 4;
          case "best_effort":
            return 5;
          case "record":
            return 6;
          default:
            return 99;
        }
      };
      efforts.forEach((effort) => {
        if (!effort.achievements || effort.achievements.length === 0) return;
        let bestAchievement = effort.achievements.sort(
          (a, b) => a.rank - b.rank
        )[0];
        let achievementText = "";
        let type = "";
        if (bestAchievement.rank === 1) {
          type = details.athlete.sex === "F" ? "qom" : "kom";
          const title = type.toUpperCase();
          achievementText = `${title} on '${
            effort.name
          }': ${this.formatEffortTime(effort.elapsed_time)} 👑`;
        } else if (bestAchievement.rank > 1 && bestAchievement.rank <= 10) {
          type = "top10";
          achievementText = `${this.getOrdinal(
            bestAchievement.rank
          )} place on '${effort.name}': ${this.formatEffortTime(
            effort.elapsed_time
          )} 🏆`;
        }
        if (achievementText) {
          options.push({
            id: `segment_${effort.id}`,
            text: achievementText,
            selected: true,
            type,
            priority: getPriority(type),
          });
        }
      });
      bestEfforts.forEach((best) => {
        let medal = "";
        let type = "best_effort";
        const prAchievement = (details.achievements || []).find(
          (a) => a.type === "best_effort" && a.name === best.name
        );
        if (
          prAchievement &&
          prAchievement.rank >= 1 &&
          prAchievement.rank <= 3
        ) {
          const medals = ["🥇", "🥈", "🥉"];
          medal = ` ${medals[prAchievement.rank - 1]}`;
          type = "best_effort_top3";
        }
        options.push({
          id: `best_${best.id}`,
          text: `Fastest ${best.name} Effort: ${this.formatEffortTime(
            best.elapsed_time
          )}${medal}`,
          selected: true,
          type,
          priority: getPriority(type),
        });
      });
      if (details.is_record) {
        const type = "record";
        options.push({
          id: "record_distance",
          text: `Longest ${details.type} Ever! 🚀`,
          selected: true,
          type,
          priority: getPriority(type),
        });
      }
      options.sort((a, b) => a.priority - b.priority);
      options.forEach((opt, index) => {
        opt.order = index;
      });
      this.achievements = options;
    },

    handleBadgeTileClick() {
      this.badgeListElement.visible = true;
      this.selectElement("badgeList");
    },

    removeBadgeList() {
      this.badgeListElement.visible = false;
      this.deselectAll();
    },

    getAllVisibleElements() {
      const elements = [];
      if (this.mapElement.visible) elements.push(this.mapElement);
      if (this.dataFields.visible) elements.push(this.dataFields);
      if (this.badgeListElement.visible) elements.push(this.badgeListElement);
      elements.push(...this.visibleGraphElements);
      elements.push(...this.textBoxes);
      elements.push(...this.photoElements);
      elements.push(...this.qrCodeElements);
      return elements;
    },

    bringToFront() {
      const activeEl = this.activeElementObject;
      if (!activeEl) return;
      this.zIndexCounter++;
      activeEl.zIndex = this.zIndexCounter;
    },

    sendToBack() {
      const activeEl = this.activeElementObject;
      if (!activeEl) return;
      const allElements = this.getAllVisibleElements();
      if (allElements.length < 2) return;
      const minZ = Math.min(...allElements.map((el) => el.zIndex));
      activeEl.zIndex = minZ - 1;
    },

    bringForward() {
      const activeEl = this.activeElementObject;
      if (!activeEl) return;
      const sortedElements = this.getAllVisibleElements().sort(
        (a, b) => a.zIndex - b.zIndex
      );
      const currentIndex = sortedElements.findIndex(
        (el) => el.id === activeEl.id
      );

      if (currentIndex < sortedElements.length - 1) {
        const elementAbove = sortedElements[currentIndex + 1];
        const tempZ = activeEl.zIndex;
        activeEl.zIndex = elementAbove.zIndex;
        elementAbove.zIndex = tempZ;
      }
    },

    sendBackward() {
      const activeEl = this.activeElementObject;
      if (!activeEl) return;
      const sortedElements = this.getAllVisibleElements().sort(
        (a, b) => a.zIndex - b.zIndex
      );
      const currentIndex = sortedElements.findIndex(
        (el) => el.id === activeEl.id
      );

      if (currentIndex > 0) {
        const elementBelow = sortedElements[currentIndex - 1];
        const tempZ = activeEl.zIndex;
        activeEl.zIndex = elementBelow.zIndex;
        elementBelow.zIndex = tempZ;
      }
    },

    clearCanvas() {
      if (
        !confirm(
          "Are you sure you want to clear the entire canvas? This action cannot be undone."
        )
      ) {
        return;
      }
      localStorage.removeItem("autosavedDesign");
      this.isApplyingState = true;
      this.mapElement.visible = false;
      this.dataFields.visible = false;
      this.badgeListElement.visible = false;
      this.weatherElement.visible = false;
      this.resetMap();
      this.dataFields = {
        ...this.dataFields,
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
      };
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
      if (!this.selectedElement) return;
      const deleteActions = {
        map: this.hideMap,
        dataFields: this.hideDataFields,
        graph: this.removeSelectedGraph,
        textBox: this.removeSelectedTextBox,
        photo: this.removeSelectedPhoto,
        badgeList: this.removeBadgeList,
        qrCode: this.removeSelectedQrCode,
        weather: this.hideWeather,
      };
      if (deleteActions[this.selectedElement]) {
        deleteActions[this.selectedElement]();
      }
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
      const deleteActions = {
        map: this.hideMap,
        dataFields: this.hideDataFields,
        graph: this.removeSelectedGraph,
        textBox: this.removeSelectedTextBox,
        photo: this.removeSelectedPhoto,
        badgeList: this.removeBadgeList,
        qrCode: this.removeSelectedQrCode,
      };
      if (deleteActions[this.selectedElement]) {
        deleteActions[this.selectedElement]();
      }
    },

    pasteElement() {
      if (!this.clipboard) return;
      const newElement = JSON.parse(JSON.stringify(this.clipboard.element));
      newElement.id = `${this.clipboard.type}_${Date.now()}`;
      newElement.x += 20;
      newElement.y += 20;
      newElement.zIndex = ++this.zIndexCounter;
      switch (this.clipboard.type) {
        case "graph":
          this.graphElements.push(newElement);
          break;
        case "textBox":
          this.textBoxes.push(newElement);
          break;
        case "photo":
          this.photoElements.push(newElement);
          break;
        case "qrCode":
          this.qrCodeElements.push(newElement);
          break;
      }
      this.$nextTick(() => {
        this.selectElement(this.clipboard.type, newElement);
      });
    },

    handleKeyDown(event) {
      const activeEl = document.activeElement;
      if (["INPUT", "TEXTAREA"].includes(activeEl.tagName)) {
        return;
      }
      if (
        ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)
      ) {
        event.preventDefault();
        if (!this.activeElementObject) return;
        const amount = event.shiftKey ? 10 : 1;
        const elementToMove = this.activeElementObject;

        switch (event.key) {
          case "ArrowUp":
            elementToMove.y -= amount;
            break;
          case "ArrowDown":
            elementToMove.y += amount;
            break;
          case "ArrowLeft":
            elementToMove.x -= amount;
            break;
          case "ArrowRight":
            elementToMove.x += amount;
            break;
        }
      } else if (event.ctrlKey && event.key.toLowerCase() === "z") {
        event.preventDefault();
        this.undo();
      } else if (event.ctrlKey && event.key.toLowerCase() === "y") {
        event.preventDefault();
        this.redo();
      } else if (event.ctrlKey && event.key.toLowerCase() === "c") {
        event.preventDefault();
        this.copyElement();
      } else if (event.ctrlKey && event.key.toLowerCase() === "x") {
        event.preventDefault();
        this.cutElement();
      } else if (event.ctrlKey && event.key.toLowerCase() === "v") {
        event.preventDefault();
        this.pasteElement();
      } else if (event.key === "Delete" && this.selectedElement) {
        event.preventDefault();
        this.deleteSelectedElement();
      } else if (event.key === "Escape") {
        event.preventDefault();
        this.deselectAll();
      }
    },

    loadState(state) {
      this.isApplyingState = true;
      if (state.mapSettings) {
        this.mapLineColor = state.mapSettings.lineColor;
        this.mapLineWeight = state.mapSettings.lineWeight;
        this.mapGradientData = state.mapSettings.gradientData;
        this.mapStyle = state.mapSettings.style;
        this.mapVisuals = state.mapSettings.visuals;
        this.fadeEdges = state.mapSettings.fadeEdges;
      }
      this.mapElement = JSON.parse(JSON.stringify(state.mapElement));
      this.dataFields = JSON.parse(JSON.stringify(state.dataFields));
      this.graphElements = JSON.parse(
        JSON.stringify(state.graphElements || [])
      );
      this.textBoxes = JSON.parse(JSON.stringify(state.textBoxes || []));
      this.photoElements = JSON.parse(
        JSON.stringify(state.photoElements || [])
      );
      if (state.badgeListElement) {
        this.badgeListElement = JSON.parse(
          JSON.stringify(state.badgeListElement)
        );
      }
      this.qrCodeElements = JSON.parse(
        JSON.stringify(state.qrCodeElements || [])
      );
      if (state.weatherElement) {
        this.weatherElement = JSON.parse(JSON.stringify(state.weatherElement));
      }
      this.$nextTick(() => {
        if (this.map) this.map.invalidateSize();
        this.isApplyingState = false;
      });
    },

    undo() {
      if (this.historyIndex > 0) {
        this.historyIndex--;
        this.loadState(this.history[this.historyIndex]);
      }
    },

    redo() {
      if (this.historyIndex < this.history.length - 1) {
        this.historyIndex++;
        this.loadState(this.history[this.historyIndex]);
      }
    },

    alignElement(direction) {
      const element = this.activeElementObject;
      const canvas = this.$refs.tshirtMockup;
      if (!element || !canvas) return;
      const canvasRect = canvas.getBoundingClientRect();
      const canvasWidth = canvasRect.width;
      const canvasHeight = canvasRect.height;
      let newX = element.x;
      let newY = element.y;
      switch (direction) {
        case "left":
          newX = -(canvasWidth / 2) + element.width / 2;
          break;
        case "center-h":
          newX = 0;
          break;
        case "right":
          newX = canvasWidth / 2 - element.width / 2;
          break;
        case "top":
          newY = -(canvasHeight / 2) + element.height / 2;
          break;
        case "center-v":
          newY = 0;
          break;
        case "bottom":
          newY = canvasHeight / 2 - element.height / 2;
          break;
      }
      element.x = newX;
      element.y = newY;
    },

    handlePhotoUpload(event) {
      if (!this.selectedPhoto) {
        alert("Please select a photo element on the canvas first.");
        event.target.value = "";
        return;
      }
      const file = event.target.files[0];
      if (file) {
        if (!file.type.startsWith("image/")) {
          alert("Please select an image file (e.g., JPG, PNG, GIF).");
          event.target.value = "";
          return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
          this.selectedPhoto.src = e.target.result;
        };
        reader.readAsDataURL(file);
      }
      event.target.value = "";
    },

    selectActivityPhoto(photo) {
      if (!this.selectedPhoto) return;
      this.selectedPhoto.src = photo.urls["600"];
    },

    handlePhotoTileClick() {
      this.selectedElement = "photo";
      if (this.photoElements.length === 0) {
        this.addPhotoElement();
      } else if (this.selectedPhotoIndex === null) {
        this.selectedPhotoIndex = 0;
      }
    },

    addPhotoElement() {
      if (this.photoElements.length >= 3) return;
      const newPhoto = {
        id: `photo_${Date.now()}`,
        src: null,
        x: 100,
        y: 100,
        width: 300,
        height: 200,
        zIndex: this.zIndexCounter++,
        mask: "none",
        filter: "none",
      };
      this.photoElements.push(newPhoto);
      this.selectElement("photo", newPhoto);
    },

    removeSelectedPhoto() {
      if (this.selectedPhotoIndex === null) return;
      this.photoElements.splice(this.selectedPhotoIndex, 1);
      this.deselectAll();
    },

    getPhotoElementStyle(photo) {
      const style = {
        transform: `translate(-50%, -50%) translate(${photo.x}px, ${photo.y}px)`,
        width: `${photo.width}px`,
        height: `${photo.height}px`,
        zIndex: photo.zIndex,
        cursor:
          this.activeInteraction.target === "photo" &&
          this.activeInteraction.index === this.photoElements.indexOf(photo)
            ? "grabbing"
            : "grab",
      };
      const masks = {
        circle: "circle(50% at 50% 50%)",
        hexagon:
          "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
        arch: 'path("M 0 200 C 0 100, 100 0, 200 0 C 300 0, 400 100, 400 200 Z")',
      };
      if (photo.mask && masks[photo.mask]) {
        style.clipPath = masks[photo.mask];
      }
      return style;
    },

    handleTextBoxTileClick() {
      this.selectedElement = "textBox";
      if (this.textBoxes.length === 0) {
        this.addTextBox();
      } else if (this.selectedTextBoxIndex === null) {
        this.selectedTextBoxIndex = 0;
      }
    },

    addTextBox() {
      if (this.textBoxes.length >= 3) return;
      const newTextBox = {
        id: `text_${Date.now()}`,
        text: this.activityData?.details?.name || "Your Title Here",
        x: 50,
        y: 50,
        width: 350,
        height: 80,
        fontFamily: "Arial",
        fontSize: 48,
        fontColor: "#333333",
        textAlign: "center",
        isBold: false,
        isItalic: false,
        zIndex: this.zIndexCounter++,
      };
      this.textBoxes.push(newTextBox);
      this.selectElement("textBox", newTextBox);
    },

    removeSelectedTextBox() {
      if (this.selectedTextBoxIndex === null) return;
      this.textBoxes.splice(this.selectedTextBoxIndex, 1);
      this.deselectAll();
    },

    getTextBoxStyle(box) {
      const index = this.textBoxes.indexOf(box);
      return {
        transform: `translate(-50%, -50%) translate(${box.x}px, ${box.y}px)`,
        width: `${box.width}px`,
        height: `${box.height}px`,
        backgroundColor: "transparent",
        borderStyle:
          this.selectedTextBox && this.selectedTextBox.id === box.id
            ? "dashed"
            : "none",
        cursor:
          this.activeInteraction.type === "drag" &&
          this.activeInteraction.target === "textBox" &&
          this.activeInteraction.index === index
            ? "grabbing"
            : "grab",
        zIndex: box.zIndex,
      };
    },

    getEditableTextStyle(box) {
      const alignmentMap = {
        left: "flex-start",
        center: "center",
        right: "flex-end",
      };
      return {
        fontFamily: box.fontFamily,
        fontSize: `${box.fontSize}px`,
        color: box.fontColor,
        justifyContent: alignmentMap[box.textAlign] || "flex-start",
        fontWeight: box.isBold ? "bold" : "normal",
        fontStyle: box.isItalic ? "italic" : "normal",
        whiteSpace: "pre-wrap",
        textAlign: box.textAlign,
      };
    },

    hideMap() {
      this.mapElement.visible = false;
      this.deselectAll();
    },

    hideDataFields() {
      this.dataFields.visible = false;
      this.deselectAll();
    },

    removeSelectedGraph() {
      if (this.selectedGraphIndex === null) return;
      this.graphElements.splice(this.selectedGraphIndex, 1);
      this.deselectAll();
    },

    handleQrCodeTileClick() {
      this.selectedElement = "qrCode";
      if (this.qrCodeElements.length === 0) {
        this.addQrCode();
      } else if (this.selectedQrCodeIndex === null) {
        this.selectedQrCodeIndex = 0;
      }
    },

    async addQrCode() {
      if (!this.activityData || !this.activityData.details) {
        alert("Activity data is not available yet.");
        return;
      }
      if (this.qrCodeElements.length >= 1) return;
      const newQrCode = {
        id: `qrCode_${Date.now()}`,
        x: -150,
        y: 150,
        width: 300,
        height: 120,
        linkType: "activity",
        customLink: "",
        customLinkInput: "",
        dataUrl: null,
        showText: true,
        text: "Give me Kudos!",
        transparentBg: false,
        zIndex: this.zIndexCounter++,
      };
      this.qrCodeElements.push(newQrCode);
      await this.updateQrCodeValue(newQrCode);
      this.selectElement("qrCode", newQrCode);
    },

    removeSelectedQrCode() {
      if (this.selectedQrCodeIndex === null) return;
      this.qrCodeElements.splice(this.selectedQrCodeIndex, 1);
      this.deselectAll();
    },

    async updateQrCodeValue(qrCode) {
      if (!qrCode || !this.activityData) return;
      let url = "";
      switch (qrCode.linkType) {
        case "activity":
          url = `https://www.strava.com/activities/${this.activityData.details.id}`;
          break;
        case "profile":
          url = `https://www.strava.com/athletes/${this.activityData.details.athlete.id}`;
          break;
        case "custom":
          url = qrCode.customLink;
          break;
      }

      if (url) {
        try {
          const qrOptions = {
            errorCorrectionLevel: "H",
            margin: 1,
            width: 256,
            color: {
              dark: "#000000",
              light: qrCode.transparentBg ? "#0000" : "#FFFFFF",
            },
          };
          qrCode.dataUrl = await QRCode.toDataURL(url, qrOptions);
        } catch (err) {
          console.error("Failed to generate QR code", err);
          qrCode.dataUrl = null;
        }
      } else {
        qrCode.dataUrl = null;
      }
    },

    updateCustomQrLink() {
      if (this.selectedQrCode && this.selectedQrCode.linkType === "custom") {
        try {
          new URL(this.selectedQrCode.customLinkInput);
          this.selectedQrCode.customLink = this.selectedQrCode.customLinkInput;
          this.updateQrCodeValue(this.selectedQrCode);
        } catch (_) {
          alert("Please enter a valid URL (e.g., https://example.com)");
        }
      }
    },

    getQrCodeElementStyle(qrCode) {
      const index = this.qrCodeElements.indexOf(qrCode);
      return {
        transform: `translate(-50%, -50%) translate(${qrCode.x}px, ${qrCode.y}px)`,
        width: `${qrCode.width}px`,
        height: `${qrCode.height}px`,
        backgroundColor: "transparent",
        cursor:
          this.activeInteraction.type === "drag" &&
          this.activeInteraction.target === "qrCode" &&
          this.activeInteraction.index === index
            ? "grabbing"
            : "grab",
        zIndex: qrCode.zIndex,
      };
    },

    handleGraphTileClick() {
      this.selectedElement = "graph";
      if (this.graphElements.length === 0) {
        this.addGraph();
      } else {
        if (this.selectedGraphIndex === null) {
          this.selectedGraphIndex = 0;
        }
      }
    },

    addGraph() {
      if (this.graphElements.length >= 3) return;
      const newGraph = {
        id: `graph_${Date.now()}`,
        visible: true,
        x: 100 + this.graphElements.length * 20,
        y: 100 + this.graphElements.length * 20,
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
        showAltitudeInBackground: true,
        transparentBg: false,
        transparentFill: false,
        showXAxisTitle: true,
        showXAxisLabels: true,
        showYAxisTitle: true,
        showYAxisLabels: true,
        lineThickness: 2,
        tickFontSize: 12,
        zIndex: this.zIndexCounter++,
      };
      this.graphElements.push(newGraph);
      this.selectElement("graph", newGraph);
    },

    selectElement(type, item = null) {
      this.selectedElement = type;
      this.selectedGraphIndex = null;
      this.selectedTextBoxIndex = null;
      this.selectedPhotoIndex = null;
      this.selectedQrCodeIndex = null;

      if (type === "graph" && item) {
        this.selectedGraphIndex = this.graphElements.indexOf(item);
      } else if (type === "textBox" && item) {
        this.selectedTextBoxIndex = this.textBoxes.indexOf(item);
      } else if (type === "photo" && item) {
        this.selectedPhotoIndex = this.photoElements.indexOf(item);
      } else if (type === "qrCode" && item) {
        this.selectedQrCodeIndex = this.qrCodeElements.indexOf(item);
      } else if (type === "dataFields") {
        if (!this.dataFields.visible) {
          this.dataFields.visible = true;
        }
      } else if (type === "map") {
        this.mapElement.visible = true;
        this.$nextTick(() => {
          if (this.map) {
            this.map.invalidateSize();
          }
        });
      }
    },

    deselectAll() {
      this.selectedElement = null;
      this.selectedGraphIndex = null;
      this.selectedTextBoxIndex = null;
      this.selectedPhotoIndex = null;
      this.selectedQrCodeIndex = null;
    },

    formatEffortTime(seconds) {
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      const s = Math.round(seconds % 60);
      let timeString = `${m.toString().padStart(2, "0")}:${s
        .toString()
        .padStart(2, "0")}`;
      if (h > 0) {
        timeString = `${h.toString()}:${timeString}`;
      }
      return timeString;
    },

    formatDistance(meters) {
      if (meters === undefined) return "-";
      return `${(meters / 1000).toFixed(2)} km`;
    },

    formatTime(seconds) {
      if (seconds === undefined) return "-";
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      const s = Math.round(seconds % 60);
      let timeString = `${m.toString().padStart(2, "0")}:${s
        .toString()
        .padStart(2, "0")}`;
      if (h > 0) {
        timeString = `${h.toString()}:${timeString}`;
      }
      return timeString;
    },

    formatPace(secondsPerKm) {
      if (secondsPerKm === undefined || !isFinite(secondsPerKm)) return "-";
      const m = Math.floor(secondsPerKm / 60);
      const s = Math.round(secondsPerKm % 60);
      return `${m}:${s.toString().padStart(2, "0")} /km`;
    },

    formatSpeed(mps) {
      if (mps === undefined) return "-";
      return `${(mps * 3.6).toFixed(1)} km/h`;
    },

    formatElevation(meters) {
      if (meters === undefined) return "-";
      return `${Math.round(meters)} m`;
    },

    formatHeartRate(bpm) {
      if (bpm === undefined) return "-";
      return `${Math.round(bpm)} bpm`;
    },

    formatCadence(spm) {
      if (spm === undefined) return "-";
      return `${Math.round(spm)} spm`;
    },

    formatPower(watts) {
      if (watts === undefined) return "-";
      return `${Math.round(watts)} W`;
    },

    updateDataFields() {
      if (!this.activityData || !this.activityData.details) return;
      const data = this.activityData.details;
      this.availableDataFields.forEach((category) => {
        category.fields.forEach((field) => {
          switch (field.id) {
            case "distance":
              field.value = this.formatDistance(data.distance);
              break;
            case "time":
              field.value = this.formatTime(data.moving_time);
              break;
            case "moving_time":
              field.value = this.formatTime(data.moving_time);
              break;
            case "elapsed_time":
              field.value = this.formatTime(data.elapsed_time);
              break;
            case "elevation_gain":
              field.value = this.formatElevation(data.total_elevation_gain);
              break;
            case "max_elevation":
              field.value = this.formatElevation(data.elev_high);
              break;
            case "avg_pace":
              field.value = this.formatPace(1000 / data.average_speed);
              break;
            case "max_pace":
              field.value = this.formatPace(1000 / data.max_speed);
              break;
            case "avg_speed":
              field.value = this.formatSpeed(data.average_speed);
              break;
            case "max_speed":
              field.value = this.formatSpeed(data.max_speed);
              break;
            case "avg_hr":
              field.value = this.formatHeartRate(data.average_heartrate);
              break;
            case "max_hr":
              field.value = this.formatHeartRate(data.max_heartrate);
              break;
            case "avg_cadence":
              field.value = this.formatCadence(
                data.average_cadence ? data.average_cadence * 2 : undefined
              );
              break;
            case "max_cadence":
              field.value = this.formatCadence(
                data.max_cadence ? data.max_cadence * 2 : undefined
              );
              break;
            case "avg_power":
              field.value = this.formatPower(data.average_watts);
              break;
            case "max_power":
              field.value = this.formatPower(data.max_watts);
              break;
          }
        });
      });
    },

    getCellBorderStyle(index) {
      const style = this.dataFields.borderStyle;
      const color = this.dataFields.borderColor;
      const styles = {};
      if (style === "none" || style === "outer") {
        return styles;
      }
      const columns = this.dataFields.columns;
      const total = this.selectedDataFields.length;
      if (columns <= 0 || total === 0) return styles;
      const totalRows = Math.ceil(total / columns);
      const row = Math.floor(index / columns);
      const col = index % columns;
      const isLastCol = col === columns - 1 || index === total - 1;
      const isLastRow = row === totalRows - 1;
      if (style === "inner" || style === "all") {
        if (!isLastCol) styles.borderRight = `1.5px solid ${color}`;
        if (!isLastRow) styles.borderBottom = `1.5px solid ${color}`;
      } else if (style === "inner-minimal") {
        const bgImages = [];
        const bgPositions = [];
        const bgSizes = [];
        if (!isLastRow) {
          bgImages.push(`linear-gradient(${color}, ${color})`);
          bgPositions.push("bottom center");
          bgSizes.push("80% 1.5px");
        }
        if (!isLastCol) {
          bgImages.push(`linear-gradient(${color}, ${color})`);
          bgPositions.push("right center");
          bgSizes.push("1.5px 80%");
        }
        if (bgImages.length > 0) {
          styles.backgroundImage = bgImages.join(", ");
          styles.backgroundPosition = bgPositions.join(", ");
          styles.backgroundSize = bgSizes.join(", ");
          styles.backgroundRepeat = "no-repeat";
        }
      }
      return styles;
    },

    handleDragStart(event, field) {
      this.draggedField = field;
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", field.id);
    },

    handleDragOver(event, targetField) {
      if (!this.draggedField || this.draggedField.id === targetField.id) return;
      this.dropTargetField = targetField;
    },

    handleDrop(event) {
      if (!this.draggedField || !this.dropTargetField) return;
      event.preventDefault();
      const fields = [...this.flatDataFields];
      const draggedIndex = fields.findIndex(
        (f) => f.id === this.draggedField.id
      );
      const targetIndex = fields.findIndex(
        (f) => f.id === this.dropTargetField.id
      );
      const [draggedItem] = fields.splice(draggedIndex, 1);
      fields.splice(targetIndex, 0, draggedItem);
      fields.forEach((field, index) => {
        field.order = index + 1;
      });
      this.clearDropIndicator();
    },

    handleDragEnd() {
      this.draggedField = null;
      this.clearDropIndicator();
    },

    clearDropIndicator() {
      this.dropTargetField = null;
    },

    isDropTarget(field) {
      return this.dropTargetField && this.dropTargetField.id === field.id;
    },

    handleInteraction(event) {
      if (!this.activeInteraction.type) return;
      if (this.activeInteraction.type === "drag") this.drag(event);
      else if (this.activeInteraction.type === "resize") this.resize(event);
    },

    stopInteraction() {
      this.activeInteraction = {
        target: null,
        type: null,
        direction: null,
        index: null,
      };
    },

    startDrag(event, target, item = null) {
      if (this.activeInteraction.type === "resize") return;
      this.selectElement(target, item);
      let index = null;
      if (item && target !== "badgeList") {
        if (target === "graph") index = this.graphElements.indexOf(item);
        else if (target === "textBox") index = this.textBoxes.indexOf(item);
        else if (target === "photo") index = this.photoElements.indexOf(item);
        else if (target === "qrCode") index = this.qrCodeElements.indexOf(item);
      }

      this.activeInteraction = { target, type: "drag", index };
      this.initialMouseX = event.clientX;
      this.initialMouseY = event.clientY;

      const el = this.activeElementObject;
      if (el) {
        this.initialElementState = {
          x: el.x,
          y: el.y,
          width: el.width,
          height: el.height,
        };
      }
    },

    drag(event) {
      if (!this.activeElementObject || !this.$refs.tshirtMockup) return;

      const parentRect = this.$refs.tshirtMockup.getBoundingClientRect();
      const movementX = event.clientX - this.initialMouseX;
      const movementY = event.clientY - this.initialMouseY;

      const el = this.activeElementObject;
      let newX = this.initialElementState.x + movementX;
      let newY = this.initialElementState.y + movementY;

      const minX = -(parentRect.width / 2) + el.width / 2;
      const maxX = parentRect.width / 2 - el.width / 2;
      const minY = -(parentRect.height / 2) + el.height / 2;
      const maxY = parentRect.height / 2 - el.height / 2;

      el.x = Math.max(minX, Math.min(maxX, newX));
      el.y = Math.max(minY, Math.min(maxY, newY));
    },

    startResize(event, target, direction, item = null) {
      let index = null;
      if (item && target !== "badgeList") {
        if (target === "graph") index = this.graphElements.indexOf(item);
        else if (target === "textBox") index = this.textBoxes.indexOf(item);
        else if (target === "photo") index = this.photoElements.indexOf(item);
        else if (target === "qrCode") index = this.qrCodeElements.indexOf(item);
      }
      this.activeInteraction = { target, type: "resize", direction, index };
      this.initialMouseX = event.clientX;
      this.initialMouseY = event.clientY;

      const el = this.activeElementObject;
      if (el) {
        this.initialElementState = {
          x: el.x,
          y: el.y,
          width: el.width,
          height: el.height,
        };
      }
    },

    resize(event) {
      if (!this.activeElementObject) return;

      const { direction } = this.activeInteraction;
      const initialState = this.initialElementState;
      const movementX = event.clientX - this.initialMouseX;
      const movementY = event.clientY - this.initialMouseY;

      let newWidth = initialState.width;
      let newHeight = initialState.height;
      let newX = initialState.x;
      let newY = initialState.y;

      if (direction.includes("right")) {
        newWidth = initialState.width + movementX;
        newX = initialState.x + movementX / 2;
      }
      if (direction.includes("left")) {
        newWidth = initialState.width - movementX;
        newX = initialState.x + movementX / 2;
      }
      if (direction.includes("bottom")) {
        newHeight = initialState.height + movementY;
        newY = initialState.y + movementY / 2;
      }
      if (direction.includes("top")) {
        newHeight = initialState.height - movementY;
        newY = initialState.y + movementY / 2;
      }

      if (newWidth < this.minSize) {
        newWidth = this.minSize;
        newX =
          initialState.x +
          (newWidth - initialState.width) *
            (direction.includes("right") ? 0.5 : -0.5);
      }
      if (newHeight < this.minSize) {
        newHeight = this.minSize;
        newY =
          initialState.y +
          (newHeight - initialState.height) *
            (direction.includes("bottom") ? 0.5 : -0.5);
      }

      const el = this.activeElementObject;
      el.width = newWidth;
      el.height = newHeight;
      el.x = newX;
      el.y = newY;

      this.$nextTick(() => {
        if (this.map) this.map.invalidateSize();
      });
    },

    getGraphElementStyle(graph) {
      const index = this.graphElements.indexOf(graph);
      return {
        transform: `translate(-50%, -50%) translate(${graph.x}px, ${graph.y}px)`,
        cursor:
          this.activeInteraction.type === "drag" &&
          this.activeInteraction.target === "graph" &&
          this.activeInteraction.index === index
            ? "grabbing"
            : "grab",
        width: `${graph.width}px`,
        height: `${graph.height}px`,
        zIndex: graph.zIndex,
      };
    },

    initMap() {
      if (
        !this.activityData ||
        !this.activityData.streams.latlng.data.length ||
        !this.$refs.mapContainer
      )
        return;
      this.map = L.map(this.$refs.mapContainer, {
        attributionControl: false,
        zoomControl: false,
        dragging: false,
        scrollWheelZoom: false,
        zoomDelta: 0.25,
        zoomSnap: 0.25,
      });
      this.map.fitBounds(this.activityData.streams.latlng.data);
      this.updateMapTileLayer();
      this.updateMap();
    },

    updateMapTileLayer() {
      if (this.currentTileLayer) this.map.removeLayer(this.currentTileLayer);
      let url = "";
      if (this.mapStyle === "standard")
        url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
      else if (this.mapStyle === "satellite")
        url =
          "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
      if (url)
        this.currentTileLayer = L.tileLayer(url, { attribution: "" }).addTo(
          this.map
        );
    },

    updateMap() {
      this.mapPolylines.forEach((p) => this.map.removeLayer(p));
      this.mapPolylines = [];

      this.updateStartEndMarkers();

      if (this.mapGradientData === "none") this.drawSolidLine();
      else this.drawGradientLine();
    },

    drawSolidLine() {
      const latlngs = this.activityData.streams.latlng.data;
      const polyline = L.polyline(latlngs, {
        color: this.mapLineColor,
        weight: this.mapLineWeight,
        opacity: 0.7,
      }).addTo(this.map);
      this.mapPolylines.push(polyline);
    },

    drawGradientLine() {
      const streamKey = this.mapGradientData;
      const dataKey = streamKey === "distance" ? "distance" : streamKey;
      const latlngs = this.activityData.streams.latlng.data;
      const rawData = this.activityData.streams[dataKey]?.data;
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
          weight: this.mapLineWeight,
          opacity: 0.85,
        }).addTo(this.map);
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

    resetMap() {
      Object.assign(this.mapElement, {
        x: 0,
        y: 0,
        width: 540,
        height: 525,
      });
      Object.assign(this, {
        mapLineColor: "#ff0000",
        mapLineWeight: 3,
        mapGradientData: "none",
        mapStyle: "standard",
        mapVisuals: "standard",
        fadeEdges: false,
      });
      if (this.map) this.map.fitBounds(this.activityData.streams.latlng.data);
      this.updateMapTileLayer();
      this.updateMap();
      this.$nextTick(() => {
        if (this.map) this.map.invalidateSize();
      });
    },

    zoomIn() {
      if (this.map) this.map.zoomIn();
    },

    zoomOut() {
      if (this.map) this.map.zoomOut();
    },
  },

  async mounted() {
    window.addEventListener("keydown", this.handleKeyDown);

    const gpxKey = this.$route.query.gpx_key;
    const designIdToLoad = this.$route.query.design_id;
    const postLoginAction = this.$route.query.action;

    // First, fetch the necessary activity data (either from Strava or GPX)
    if (gpxKey) {
      console.log("Loading design from GPX data key:", gpxKey);
      const gpxDataString = localStorage.getItem(gpxKey);
      if (gpxDataString) {
        this.activityData = JSON.parse(gpxDataString);
        localStorage.removeItem(gpxKey);
      }
    } else if (this.activityId) {
      try {
        const response = await axios.get(
          `http://localhost:5000/api/activities/${this.activityId}`,
          { withCredentials: true }
        );
        this.activityData = response.data;
        this.activityPhotos = response.data.photos || [];
      } catch (error) {
        console.error("Error fetching activity data:", error);
      }
    }

    // Now, decide what design state to load into the editor
    if (designIdToLoad) {
      // Editing an existing design from "My Designs"
      try {
        const response = await axios.get(
          `http://localhost:5000/api/designs/${designIdToLoad}`,
          { withCredentials: true }
        );
        this.loadState(response.data.design_data);
      } catch (error) {
        console.error("Failed to load existing design:", error);
      }
    } else if (postLoginAction === "save") {
      // User just logged in to save their GPX design
      const unsavedDesign = localStorage.getItem("unsavedGpxDesign");
      if (unsavedDesign) {
        this.loadState(JSON.parse(unsavedDesign));
        // Now that the state is loaded, automatically trigger the save
        this.saveDesign();
      }
    } else {
      // Standard flow: check for a locally autosaved design
      const autosavedDesign = localStorage.getItem("autosavedDesign");
      if (autosavedDesign) {
        this.loadState(JSON.parse(autosavedDesign));
      }
    }

    this.loading = false;
  },

  beforeUnmount() {
    if (this.map) {
      this.map.remove();
    }
    window.removeEventListener("keydown", this.handleKeyDown);
  },
};
</script>

<style scoped>
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

.editor-sidebar {
  width: 250px;
  background-color: #ffffff;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  border-right: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.editor-tools-sidebar {
  width: 200px;
  background-color: #ffffff;
  padding: 20px;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  border-left: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.editor-tools-sidebar h2 {
  margin-top: 0;
  color: #333;
}

.tools-section {
  margin-bottom: 20px;
}

.element-box {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.element-box.active {
  border-color: #4287f5;
  box-shadow: 0 0 5px rgba(66, 135, 245, 0.5);
}

.element-box:hover {
  background-color: #f1f1f1;
  border-color: #ccc;
}

.element-box > p {
  text-align: center;
  margin: 0;
  font-weight: bold;
}

.map-options,
.data-fields-options {
  text-align: left;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
  cursor: default;
}

.map-options label,
.data-fields-options label {
  display: block;
  font-size: 0.9em;
  margin-bottom: 5px;
  color: #555;
}

.map-options select,
.map-options input,
.data-fields-options select {
  width: 90%;
  margin-bottom: 10px;
}

.map-options .color-picker {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-color: transparent;
  border: none;
  cursor: pointer;
  height: 30px;
  width: 30px;
  padding: 0;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: 0 0 0 1px #ddd;
}

.map-options .color-picker::-webkit-color-swatch,
.map-options .color-picker::-moz-color-swatch {
  border: none;
  border-radius: 5px;
}

.map-options .range-slider {
  vertical-align: middle;
  width: 70%;
  margin-right: 5px;
}

.editor-canvas-container {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  overflow: auto;
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
  background-color: #ddd;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
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

#map {
  position: relative;
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

.fade-option,
.field-option {
  margin-top: 10px;
  display: flex;
  align-items: center;
}

.fade-option label,
.field-option label {
  margin-right: 10px;
  margin-bottom: 0;
  display: inline-block;
  cursor: pointer;
  flex-grow: 1;
}

.fade-option input:disabled + label {
  color: #aaa;
  cursor: not-allowed;
  pointer-events: none;
}

.field-option input {
  width: auto;
  margin-right: 8px;
  margin-bottom: 0;
  cursor: pointer;
}

.zoom-controls {
  margin-bottom: 10px;
}

.zoom-buttons {
  display: flex;
  gap: 10px;
}

.zoom-button {
  width: 35px;
  height: 30px;
  border: none;
  background-color: #4287f5;
  color: white;
  cursor: pointer;
  font-size: 1.2em;
  font-weight: bold;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.zoom-button:hover {
  background-color: #3367d6;
}

.category-group {
  margin-top: 10px;
}

.category-title {
  font-weight: bold;
  font-size: 0.95em;
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.button-grid-tools {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
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

.field-option {
  display: flex;
  align-items: center;
  position: relative;
  padding: 4px 0;
}

.drag-handle {
  cursor: grab;
  padding: 4px 8px 4px 0;
  color: #aaa;
  font-size: 1.2em;
  line-height: 1;
}

.drag-handle:active {
  cursor: grabbing;
}

.drop-indicator {
  position: absolute;
  top: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #4287f5;
  visibility: hidden;
}

.option-group {
  margin-top: 15px;
}

.style-group {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.style-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-picker-small {
  width: 30px !important;
  height: 30px !important;
  margin-bottom: 0 !important;
  cursor: pointer;
  border: none;
  padding: 0;
  background: transparent;
}

.range-slider-small {
  width: 100px !important;
  margin: 0 !important;
}

.design-area.is-transparent {
  background-color: transparent !important;
}

.design-area.no-map-bg {
  background-color: transparent !important;
}

.design-area.no-map-bg #map .leaflet-container {
  background-color: transparent !important;
}

.design-area.fade-active {
  background-color: transparent;
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

.fade-option input:disabled + label {
  color: #aaa;
  cursor: not-allowed;
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

.design-area {
  border: 2px dashed transparent;
}

.design-area.selected {
  border-color: #4287f5;
}

.button-group button {
  padding: 5px 10px;
  margin-right: 5px;
  border: 1px solid #ccc;
  background-color: #f0f0f0;
  cursor: pointer;
}

.button-group button:hover {
  background-color: #e0e0e0;
}

.button-group button.active {
  background-color: #4287f5;
  color: white;
  border-color: #3367d6;
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

.photo-selection-container {
  margin-top: 10px;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 10px;
}

.photo-thumbnail {
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 4px;
  overflow: hidden;
  aspect-ratio: 1 / 1;
  transition: border-color 0.2s;
}

.photo-thumbnail:hover {
  border-color: #4287f5;
}

.photo-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-photos-message {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 0.9em;
  color: #888;
  margin: 10px 0;
}

.photo-upload-container {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.photo-upload-container .upload-button {
  background-color: #007bff;
  color: white;
}

.upload-button:hover {
  background-color: #0056b3;
}

label.sidebar-button {
  display: block;
  text-align: center;
}

.button-grid-tools.align-grid {
  grid-template-columns: repeat(3, 1fr);
}

.button-grid-tools.layer-grid {
  grid-template-columns: repeat(2, 1fr);
}

.tool-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  font-size: 0.8em;
  cursor: pointer;
  padding: 8px 5px;
  border-radius: 5px;
  transition: background-color 0.2s, border-color 0.2s;
  color: #333;
  min-height: 50px;
  text-align: center;
}

.tool-button svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.tool-button:hover:not(:disabled) {
  background-color: #f0f0f0;
  border-color: #4287f5;
}

.tool-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f5f5f5;
}

.save-button {
  width: 100%;
  flex-direction: row;
  gap: 8px;
  background-color: #28a745;
  color: white;
  border-color: #28a745;
  font-weight: bold;
}

.save-button:hover {
  background-color: #218838;
  border-color: #218838;
}
.align-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
}

.align-button svg {
  fill: #333;
}

.clear-all-button {
  width: 100%;
  flex-direction: row;
  gap: 8px;
  background-color: #dc3545;
  color: white;
  border-color: #dc3545;
  font-weight: bold;
}

.clear-all-button:hover:not(:disabled) {
  background-color: #c82333;
  border-color: #c82333;
}

.custom-link-input {
  display: flex;
  align-items: center;
  gap: 5px;
}

.custom-link-input input {
  flex-grow: 1;
  width: calc(100% - 40px);
  margin-bottom: 0 !important;
}

.confirm-button {
  width: 30px;
  height: 30px;
  border: 1px solid #1e7e34;
  background-color: #28a745;
  color: white;
  cursor: pointer;
  border-radius: 5px;
  font-size: 1.2em;
  font-weight: bold;
  padding: 0;
  line-height: 28px;
  flex-shrink: 0;
  transition: background-color 0.2s;
}

.confirm-button:hover {
  background-color: #218838;
}

.qr-code-area {
  background-color: transparent !important;
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
  white-space: nowrap;
}
.badges-options .category-title {
  margin-bottom: 10px;
  font-size: 0.9em;
  color: #555;
}

.achievements-options,
.badge-edit-options {
  text-align: left;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
  cursor: default;
}

.achievement-list {
  max-height: 150px;
  overflow-y: auto;
  padding-right: 5px;
  margin-bottom: 15px;
}

.badge-options .style-controls {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
}
.badge-options .option-group-inline {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}
.badge-options .option-group-inline label {
  font-size: 0.8em;
  margin-bottom: 0;
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

.weather-options {
  text-align: left;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
  cursor: default;
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
  /* Creëert een schaakbordpatroon */
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

.route-flag-marker svg {
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.4));
}
</style>
