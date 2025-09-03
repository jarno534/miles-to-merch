<template>
  <div class="editor-sidebar">
    <div class="placement-controls-wrapper">
      <h2>Placement</h2>
      <div
        class="placement-controls"
        v-if="editorProductData && editorProductData.print_areas"
      >
        <button
          v-for="(area, key) in editorProductData.print_areas"
          :key="key"
          @click="$emit('update:activePlacement', key)"
          :class="{ active: activePlacement === key }"
        >
          {{ area.name || key }}
        </button>
      </div>
    </div>

    <h2>Design Elements</h2>
    <div
      :class="{ active: selection.type === 'map' }"
      class="element-box"
      @click="$emit('select-element', 'map')"
    >
      <p>Map</p>
      <div v-if="selection.type === 'map'" @click.stop class="map-options">
        <label for="mapStyle">Map Style:</label>
        <select
          id="mapStyle"
          :value="mapSettings.style"
          @change="updateMapSetting('style', $event.target.value)"
        >
          <option v-for="(layer, key) in tileLayers" :key="key" :value="key">
            {{ layer.name }}
          </option>
          <option value="none">No Map Background</option>
        </select>
        <template v-if="mapSettings.style !== 'none'">
          <label for="mapVisuals">Map Visuals:</label>
          <select
            id="mapVisuals"
            :value="mapSettings.visuals"
            @change="updateMapSetting('visuals', $event.target.value)"
          >
            <option value="standard">Standard Color</option>
            <option value="grayscale">Grayscale</option>
            <option value="blue">Blue</option>
            <option value="pink">Pink</option>
            <option value="sepia">Sepia</option>
            <option value="vivid">Vivid</option>
          </select>
        </template>
        <label for="gradientData">Color based on:</label>
        <select
          id="gradientData"
          :value="mapSettings.gradientData"
          @change="
            $emit('update:mapSettings', {
              ...mapSettings,
              gradientData: $event.target.value,
            })
          "
        >
          <option
            v-for="opt in availableGradientOptions"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.text }}
          </option>
        </select>
        <template v-if="mapSettings.gradientData === 'none'">
          <label for="lineColor">Line Color:</label>
          <input
            type="color"
            id="lineColor"
            :value="mapSettings.lineColor"
            @input="updateMapSetting('lineColor', $event.target.value)"
            class="color-picker"
          />
        </template>
        <label for="lineWeight">Line Weight:</label>
        <input
          type="range"
          id="lineWeight"
          min="1"
          max="10"
          :value="mapSettings.lineWeight"
          @input="
            $emit('update:mapSettings', {
              ...mapSettings,
              lineWeight: +$event.target.value,
            })
          "
          class="range-slider"
        />
        <div class="field-option">
          <input
            type="checkbox"
            id="showStartEndMarkers"
            :checked="mapSettings.showStartEndMarkers"
            @change="
              updateMapSetting('showStartEndMarkers', $event.target.checked)
            "
          />
          <label for="showStartEndMarkers">Start/End Markers</label>
        </div>
        <div class="field-option">
          <input
            type="checkbox"
            id="fadeEdges"
            :checked="mapSettings.fadeEdges"
            @change="
              $emit('update:mapSettings', {
                ...mapSettings,
                fadeEdges: $event.target.checked,
              })
            "
            :disabled="mapSettings.style === 'none'"
          />
          <label for="fadeEdges">Fade Edges</label>
        </div>
        <template v-if="mapSettings.style === '3d-terrain'">
          <label for="mapPitch">Tilt Angle: {{ mapSettings.pitch }}°</label>
          <input
            type="range"
            id="mapPitch"
            min="0"
            max="85"
            :value="mapSettings.pitch"
            @input="updateMapSetting('pitch', +$event.target.value)"
            class="range-slider"
          />

          <label for="mapBearing">Rotation: {{ mapSettings.bearing }}°</label>
          <input
            type="range"
            id="mapBearing"
            min="-180"
            max="180"
            :value="mapSettings.bearing"
            @input="updateMapSetting('bearing', +$event.target.value)"
            class="range-slider"
          />
        </template>
        <div class="pan-controls">
          <label>Pan Map:</label>
          <div class="pan-grid">
            <div></div>
            <button @click="$emit('pan-map', 'up')" class="pan-button">
              ↑
            </button>
            <div></div>
            <button @click="$emit('pan-map', 'left')" class="pan-button">
              ←
            </button>
            <button
              @click="$emit('pan-map', 'center')"
              class="pan-button center-button"
            ></button>
            <button @click="$emit('pan-map', 'right')" class="pan-button">
              →
            </button>
            <div></div>
            <button @click="$emit('pan-map', 'down')" class="pan-button">
              ↓
            </button>
            <div></div>
          </div>
        </div>
        <div class="zoom-controls">
          <label>Zoom Level:</label>
          <div class="zoom-buttons">
            <button @click="$emit('zoom-in')" class="zoom-button">+</button>
            <button @click="$emit('zoom-out')" class="zoom-button">-</button>
          </div>
        </div>
        <button
          class="sidebar-button remove-button"
          @click.stop="$emit('remove-element', { id: 'map' })"
        >
          Delete Map
        </button>
      </div>
    </div>

    <div
      :class="{ active: selection.type === 'dataFields' }"
      class="element-box"
      @click="$emit('select-element', 'dataFields')"
    >
      <p>Data Fields</p>
      <div
        v-if="selection.type === 'dataFields'"
        @click.stop
        class="data-fields-options"
      >
        <div class="option-group">
          <label for="dataColumns">Columns:</label>
          <select
            id="dataColumns"
            :value="dataFields.columns"
            @change="
              $emit('update:dataFields', {
                ...dataFields,
                columns: +$event.target.value,
              })
            "
          >
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
          </select>
        </div>
        <div class="option-group">
          <label for="dataBorderStyle">Border Style:</label>
          <select
            id="dataBorderStyle"
            :value="dataFields.borderStyle"
            @change="
              $emit('update:dataFields', {
                ...dataFields,
                borderStyle: $event.target.value,
              })
            "
          >
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
              :value="dataFields.labelColor"
              @input="
                $emit('update:dataFields', {
                  ...dataFields,
                  labelColor: $event.target.value,
                })
              "
              class="color-picker-small"
            />
            <input
              type="range"
              min="8"
              max="24"
              :value="dataFields.labelSize"
              @input="
                $emit('update:dataFields', {
                  ...dataFields,
                  labelSize: +$event.target.value,
                })
              "
              class="range-slider-small"
            />
          </div>
        </div>
        <div class="style-group">
          <label>Value Style</label>
          <div class="style-controls">
            <input
              type="color"
              :value="dataFields.valueColor"
              @input="
                $emit('update:dataFields', {
                  ...dataFields,
                  valueColor: $event.target.value,
                })
              "
              class="color-picker-small"
            />
            <input
              type="range"
              min="10"
              max="48"
              :value="dataFields.valueSize"
              @input="
                $emit('update:dataFields', {
                  ...dataFields,
                  valueSize: +$event.target.value,
                })
              "
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
              :checked="field.selected"
              @change="toggleDataField(field, $event.target.checked)"
              @click.stop
            />
            <label :for="field.id">{{ field.label }}</label>
          </div>
        </div>
        <button
          class="sidebar-button remove-button"
          @click.stop="$emit('remove-element', { id: 'dataFields' })"
        >
          Delete Data Fields
        </button>
      </div>
    </div>

    <div
      :class="{ active: selection.type === 'graph' }"
      class="element-box"
      @click="$emit('select-element', 'graph')"
    >
      <p>Graph</p>
      <div
        v-if="selection.type === 'graph' && selectedGraph"
        @click.stop
        class="data-fields-options"
      >
        <div class="option-group">
          <label for="graphData">Data Source:</label>
          <select
            id="graphData"
            :value="selectedGraph.selectedDataSource"
            @change="
              updateGraphProperty('selectedDataSource', $event.target.value)
            "
          >
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
          <label><b>Styling</b></label>
          <div class="option-group">
            <label>Line Color:</label>
            <input
              type="color"
              :value="selectedGraph.lineColor"
              @input="updateGraphProperty('lineColor', $event.target.value)"
              class="color-picker"
            />
          </div>
          <div class="option-group">
            <label>Line Thickness:</label>
            <input
              type="range"
              :value="selectedGraph.lineThickness"
              @input="
                updateGraphProperty('lineThickness', +$event.target.value)
              "
              min="1"
              max="10"
              class="range-slider"
            />
          </div>
          <div class="field-option">
            <input
              type="checkbox"
              :id="`transparentFill-${selectedGraph.id}`"
              :checked="selectedGraph.transparentFill"
              @change="
                updateGraphProperty('transparentFill', $event.target.checked)
              "
            />
            <label :for="`transparentFill-${selectedGraph.id}`"
              >Transparent Fill</label
            >
          </div>
          <div v-if="!selectedGraph.transparentFill" class="option-group">
            <label>Fill Color:</label>
            <input
              type="color"
              :value="selectedGraph.fillColor"
              @input="updateGraphProperty('fillColor', $event.target.value)"
              class="color-picker"
            />
          </div>
          <div class="option-group">
            <label>Axis & Grid Color:</label>
            <input
              type="color"
              :value="selectedGraph.axisColor"
              @input="updateGraphProperty('axisColor', $event.target.value)"
              class="color-picker"
            />
          </div>
        </div>

        <div class="style-group">
          <label><b>Display Options</b></label>
          <div class="field-option">
            <input
              type="checkbox"
              :id="`transparentBg-${selectedGraph.id}`"
              :checked="selectedGraph.transparentBg"
              @change="
                updateGraphProperty('transparentBg', $event.target.checked)
              "
            />
            <label :for="`transparentBg-${selectedGraph.id}`"
              >Transparent Background</label
            >
          </div>
          <div class="field-option">
            <input
              type="checkbox"
              :id="`showGrid-${selectedGraph.id}`"
              :checked="selectedGraph.showGrid"
              @change="updateGraphProperty('showGrid', $event.target.checked)"
            />
            <label :for="`showGrid-${selectedGraph.id}`">Show Grid Lines</label>
          </div>
          <div
            class="field-option"
            v-if="selectedGraph.selectedDataSource !== 'altitude'"
          >
            <input
              type="checkbox"
              :id="`showAltitude-${selectedGraph.id}`"
              :checked="selectedGraph.showAltitudeInBackground"
              @change="
                updateGraphProperty(
                  'showAltitudeInBackground',
                  $event.target.checked
                )
              "
            />
            <label :for="`showAltitude-${selectedGraph.id}`"
              >Altitude in Background</label
            >
          </div>
          <div class="field-option">
            <input
              type="checkbox"
              :id="`showLegend-${selectedGraph.id}`"
              :checked="selectedGraph.showLegend"
              @change="updateGraphProperty('showLegend', $event.target.checked)"
            />
            <label :for="`showLegend-${selectedGraph.id}`">Legend</label>
          </div>
        </div>

        <div class="style-group">
          <label><b>Axes & Labels</b></label>
          <div class="option-group">
            <label>Minimum Y-value:</label>
            <input
              type="number"
              placeholder="Auto"
              :value="selectedGraph.yAxisMin"
              @change="
                updateGraphProperty(
                  'yAxisMin',
                  $event.target.value === '' ? null : +$event.target.value
                )
              "
            />
          </div>
          <div class="option-group">
            <label>Maximum Y-value:</label>
            <input
              type="number"
              placeholder="Auto"
              :value="selectedGraph.yAxisMax"
              @change="
                updateGraphProperty(
                  'yAxisMax',
                  $event.target.value === '' ? null : +$event.target.value
                )
              "
            />
          </div>
          <div class="option-group">
            <label>Font Size Labels:</label>
            <input
              type="range"
              :value="selectedGraph.tickFontSize"
              @input="updateGraphProperty('tickFontSize', +$event.target.value)"
              min="8"
              max="20"
              class="range-slider"
            />
          </div>
          <div class="option-group">
            <label>Font Size Titles:</label>
            <input
              type="range"
              :value="selectedGraph.titleFontSize"
              @input="
                updateGraphProperty('titleFontSize', +$event.target.value)
              "
              min="8"
              max="24"
              class="range-slider"
            />
          </div>
          <div class="option-group">
            <label>Horizontal Grid Lines:</label>
            <input
              type="range"
              :value="selectedGraph.yAxisTicks"
              @input="updateGraphProperty('yAxisTicks', +$event.target.value)"
              min="2"
              max="20"
              class="range-slider"
            />
          </div>
          <div class="option-group">
            <label>Vertical Grid Lines:</label>
            <input
              type="range"
              :value="selectedGraph.xAxisTicks"
              @input="updateGraphProperty('xAxisTicks', +$event.target.value)"
              min="2"
              max="25"
              class="range-slider"
            />
          </div>
          <div class="field-option">
            <input
              type="checkbox"
              :id="`showXTitle-${selectedGraph.id}`"
              :checked="selectedGraph.showXAxisTitle"
              @change="
                updateGraphProperty('showXAxisTitle', $event.target.checked)
              "
            />
            <label :for="`showXTitle-${selectedGraph.id}`"
              >Show X-Axis Title</label
            >
          </div>
          <div class="field-option">
            <input
              type="checkbox"
              :id="`showXLabels-${selectedGraph.id}`"
              :checked="selectedGraph.showXAxisLabels"
              @change="
                updateGraphProperty('showXAxisLabels', $event.target.checked)
              "
            />
            <label :for="`showXLabels-${selectedGraph.id}`"
              >Show X-Axis Labels</label
            >
          </div>
          <div class="field-option">
            <input
              type="checkbox"
              :id="`showYTitle-${selectedGraph.id}`"
              :checked="selectedGraph.showYAxisTitle"
              @change="
                updateGraphProperty('showYAxisTitle', $event.target.checked)
              "
            />
            <label :for="`showYTitle-${selectedGraph.id}`"
              >Show Y-Axis Title</label
            >
          </div>
          <div class="field-option">
            <input
              type="checkbox"
              :id="`showYLabels-${selectedGraph.id}`"
              :checked="selectedGraph.showYAxisLabels"
              @change="
                updateGraphProperty('showYAxisLabels', $event.target.checked)
              "
            />
            <label :for="`showYLabels-${selectedGraph.id}`"
              >Show Y-Axis Labels</label
            >
          </div>
          <template
            v-if="
              selectedGraph.showAltitudeInBackground &&
              selectedGraph.selectedDataSource !== 'altitude'
            "
          >
            <div class="field-option">
              <input
                type="checkbox"
                :id="`showY1Title-${selectedGraph.id}`"
                :checked="selectedGraph.showY1AxisTitle"
                @change="
                  updateGraphProperty('showY1AxisTitle', $event.target.checked)
                "
              />
              <label :for="`showY1Title-${selectedGraph.id}`"
                >Show Altitude Title</label
              >
            </div>
            <div class="field-option">
              <input
                type="checkbox"
                :id="`showY1Labels-${selectedGraph.id}`"
                :checked="selectedGraph.showY1AxisLabels"
                @change="
                  updateGraphProperty('showY1AxisLabels', $event.target.checked)
                "
              />
              <label :for="`showY1Labels-${selectedGraph.id}`"
                >Show Altitude Labels</label
              >
            </div>
          </template>
        </div>

        <button
          v-if="graphElements.length < 3"
          @click.stop="$emit('add-element', 'graph')"
          class="sidebar-button add-button"
        >
          + Add Graph
        </button>
        <button
          class="sidebar-button remove-button"
          @click.stop="$emit('remove-element', selectedGraph)"
        >
          Delete Graph
        </button>
      </div>
    </div>

    <div
      :class="{ active: selection.type === 'textBox' }"
      class="element-box"
      @click="$emit('select-element', 'textBox')"
    >
      <p>Text Box</p>
      <div
        v-if="selection.type === 'textBox' && selectedTextBox"
        @click.stop
        class="data-fields-options"
      >
        <div class="option-group">
          <label for="textBoxContent">Text Content:</label>
          <textarea
            id="textBoxContent"
            :value="selectedTextBox.text"
            @input="updateTextBoxProperty('text', $event.target.value)"
            rows="3"
          ></textarea>
        </div>

        <div class="option-group">
          <label>Text Color:</label>
          <input
            type="color"
            :value="selectedTextBox.fontColor"
            @input="updateTextBoxProperty('fontColor', $event.target.value)"
            class="color-picker"
          />
        </div>
        <div class="field-option">
          <input
            type="checkbox"
            :id="`transparentBg-${selectedTextBox.id}`"
            :checked="selectedTextBox.transparentBg"
            @change="
              updateTextBoxProperty('transparentBg', $event.target.checked)
            "
          />
          <label :for="`transparentBg-${selectedTextBox.id}`"
            >Transparent Background</label
          >
        </div>

        <template v-if="!selectedTextBox.transparentBg">
          <div class="option-group">
            <label>Background Color:</label>
            <input
              type="color"
              :value="selectedTextBox.backgroundColor"
              @input="
                updateTextBoxProperty('backgroundColor', $event.target.value)
              "
              class="color-picker"
            />
          </div>
          <div class="option-group">
            <label>Corner Radius:</label>
            <input
              type="range"
              :value="selectedTextBox.borderRadius"
              @input="
                updateTextBoxProperty('borderRadius', +$event.target.value)
              "
              min="0"
              max="50"
              class="range-slider"
            />
          </div>
        </template>

        <div class="option-group">
          <label>Font Size:</label>
          <input
            type="range"
            :value="selectedTextBox.fontSize"
            @input="updateTextBoxProperty('fontSize', +$event.target.value)"
            min="12"
            max="120"
            class="range-slider"
          />
          <label>Font:</label>
          <select
            :value="selectedTextBox.fontFamily"
            @change="updateTextBoxProperty('fontFamily', $event.target.value)"
          >
            <option value="Arial">Arial</option>
            <option value="Verdana">Verdana</option>
            <option value="Georgia">Georgia</option>
            <option value="'Courier New', Courier, monospace">
              Courier New
            </option>
            <option value="'Times New Roman', Times, serif">
              Times New Roman
            </option>
          </select>
        </div>

        <button
          v-if="textBoxes.length < 3"
          @click.stop="$emit('add-element', 'textBox')"
          class="sidebar-button add-button"
        >
          + Add Text Box
        </button>
        <button
          class="sidebar-button remove-button"
          @click.stop="$emit('remove-element', selectedTextBox)"
        >
          Delete Text Box
        </button>
      </div>
    </div>

    <div
      :class="{ active: selection.type === 'photo' }"
      class="element-box"
      @click="$emit('select-element', 'photo')"
    >
      <p>Photo</p>
      <div
        v-if="selection.type === 'photo' && selectedPhoto"
        @click.stop
        class="data-fields-options"
      >
        <div v-if="isStravaActivity" class="photo-selection-container">
          <p class="category-title">Select from Activity</p>
          <div class="photo-grid">
            <div
              v-for="photo in activityPhotos"
              :key="photo.unique_id"
              class="photo-thumbnail"
              @click="updatePhotoProperty('src', photo.urls['600'])"
            >
              <img :src="photo.urls['600']" alt="Activity Photo Thumbnail" />
            </div>
            <p
              v-if="!activityPhotos || activityPhotos.length === 0"
              class="no-photos-message"
            >
              No photos found.
            </p>
          </div>
        </div>
        <div class="photo-upload-container">
          <p class="category-title">
            {{ isStravaActivity ? "Or Upload a Photo" : "Upload a Photo" }}
          </p>
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
          @click.stop="$emit('add-element', 'photo')"
          class="sidebar-button add-button"
        >
          + Add Photo
        </button>
        <button
          class="sidebar-button remove-button"
          @click.stop="$emit('remove-element', selectedPhoto)"
        >
          Delete Photo
        </button>
      </div>
    </div>

    <div
      v-if="isStravaActivity && achievements && achievements.length > 0"
      :class="{ active: selection.type === 'badgeList' }"
      class="element-box"
      @click="$emit('select-element', 'badgeList')"
    >
      <p>Activity Badges</p>

      <div
        v-if="selection.type === 'badgeList'"
        @click.stop
        class="badge-options"
      >
        <div class="style-group" style="text-align: left">
          <label><b>Styling</b></label>

          <div class="option-group">
            <label>Font Family:</label>
            <select
              :value="badgeListElement.fontFamily"
              @change="
                $emit('update:badgeListElement', {
                  ...badgeListElement,
                  fontFamily: $event.target.value,
                })
              "
            >
              <option value="Arial">Arial</option>
              <option value="Verdana">Verdana</option>
              <option value="Georgia">Georgia</option>
              <option value="'Courier New', Courier, monospace">
                Courier New
              </option>
              <option value="'Times New Roman', Times, serif">
                Times New Roman
              </option>
            </select>
          </div>

          <div class="option-group">
            <label>Font Size:</label>
            <input
              type="range"
              :value="badgeListElement.fontSize"
              @input="
                $emit('update:badgeListElement', {
                  ...badgeListElement,
                  fontSize: +$event.target.value,
                })
              "
              min="8"
              max="24"
              class="range-slider"
            />
          </div>

          <div class="option-group">
            <label>Text Color:</label>
            <input
              type="color"
              :value="badgeListElement.textColor"
              @input="
                $emit('update:badgeListElement', {
                  ...badgeListElement,
                  textColor: $event.target.value,
                })
              "
              class="color-picker"
            />
          </div>

          <div class="field-option">
            <input
              type="checkbox"
              id="badgeTransparentBg"
              :checked="badgeListElement.transparentBg"
              @change="
                $emit('update:badgeListElement', {
                  ...badgeListElement,
                  transparentBg: $event.target.checked,
                })
              "
            />
            <label for="badgeTransparentBg">Transparent Background</label>
          </div>

          <div v-if="!badgeListElement.transparentBg" class="option-group">
            <label>Background Color:</label>
            <input
              type="color"
              :value="badgeListElement.backgroundColor"
              @input="
                $emit('update:badgeListElement', {
                  ...badgeListElement,
                  backgroundColor: $event.target.value,
                })
              "
              class="color-picker"
            />
          </div>
        </div>

        <div class="category-group" style="text-align: left; margin-top: 20px">
          <p class="category-title">Select & Reorder Badges</p>
          <div class="achievement-list-sidebar" @dragleave="handleBadgeDragEnd">
            <div
              v-for="ach in sortedAchievements"
              :key="ach.id"
              class="field-option"
              @dragover.prevent="handleBadgeDragOver($event, ach)"
              @drop="handleBadgeDrop($event, ach)"
            >
              <div
                class="drop-indicator"
                :style="{
                  visibility:
                    dropTargetBadge && dropTargetBadge.id === ach.id
                      ? 'visible'
                      : 'hidden',
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
                :id="`ach-${ach.id}`"
                :checked="ach.selected"
                @change="toggleAchievement(ach, $event.target.checked)"
                @click.stop
              />
              <label :for="`ach-${ach.id}`">{{ ach.text }}</label>
            </div>
          </div>
        </div>
        <button
          @click.stop="$emit('remove-element', { id: 'badgeList' })"
          class="sidebar-button remove-button"
        >
          Delete Badge List
        </button>
      </div>
    </div>

    <div
      v-if="isStravaActivity"
      :class="{ active: selection.type === 'qrCode' }"
      class="element-box"
      @click="$emit('select-element', 'qrCode')"
    >
      <p>QR Code</p>
      <div
        v-if="selection.type === 'qrCode' && selectedQrCode"
        @click.stop
        class="data-fields-options"
      >
        <div class="option-group">
          <label><b>Link Destination</b></label>
          <div class="field-option">
            <input
              type="radio"
              id="qrLinkActivity"
              value="activity"
              :checked="selectedQrCode.linkType === 'activity'"
              @change="updateQrCodeProperty('linkType', 'activity')"
            />
            <label for="qrLinkActivity">Link to activity</label>
          </div>
          <div class="field-option">
            <input
              type="radio"
              id="qrLinkProfile"
              value="profile"
              :checked="selectedQrCode.linkType === 'profile'"
              @change="updateQrCodeProperty('linkType', 'profile')"
            />
            <label for="qrLinkProfile">Link to profile</label>
          </div>
          <div class="field-option">
            <input
              type="radio"
              id="qrLinkCustom"
              value="custom"
              :checked="selectedQrCode.linkType === 'custom'"
              @change="updateQrCodeProperty('linkType', 'custom')"
            />
            <label for="qrLinkCustom">Custom link</label>
          </div>
        </div>
        <div class="option-group" v-if="selectedQrCode.linkType === 'custom'">
          <label for="customQrLink">Custom URL:</label>
          <div class="custom-link-wrapper">
            <input
              type="text"
              id="customQrLink"
              v-model="localCustomLink"
              placeholder="https://..."
              @keyup.enter="updateCustomLink"
            />
            <button
              @click="updateCustomLink"
              class="link-validate-btn"
              :class="{ 'is-valid': isCustomLinkValid }"
              :disabled="!isCustomLinkValid"
              title="Bevestig URL"
            >
              ✔
            </button>
          </div>
        </div>
        <div class="option-group">
          <label for="qrCodeText"><b>Text next to QR code:</b></label>
          <textarea
            id="qrCodeText"
            :value="selectedQrCode.text"
            @input="updateQrCodeProperty('text', $event.target.value)"
            rows="2"
          ></textarea>
        </div>
        <div
          v-if="selection && selection.type === 'qrCode'"
          class="settings-block"
        >
          <div class="setting">
            <label for="qr-font-:">Font Family</label>
            <select
              id="qr-font-family"
              :value="selection.item.fontFamily"
              @change="
                $emit('update:selection-item-property', {
                  property: 'fontFamily',
                  value: $event.target.value,
                })
              "
            >
              <option>Inter</option>
              <option>Arial</option>
              <option>Verdana</option>
              <option>Georgia</option>
              <option>Times New Roman</option>
              <option>Courier New</option>
            </select>
          </div>

          <div class="setting">
            <label for="qr-font-size"
              >Font Size: {{ selection.item.fontSize }}px</label
            >
            <input
              type="range"
              id="qr-font-size"
              :value="selection.item.fontSize"
              @input="
                $emit('update:selection-item-property', {
                  property: 'fontSize',
                  value: $event.target.valueAsNumber,
                })
              "
              min="10"
              max="100"
            />
          </div>

          <div class="setting">
            <label for="qr-text-color">Text & QR Color:</label>
            <input
              type="color"
              id="qr-text-color"
              :value="selection.item.textColor"
              @input="
                $emit('update:selection-item-property', {
                  property: 'textColor',
                  value: $event.target.value,
                })
              "
              class="color-picker"
            />
          </div>

          <div class="option-group">
            <label><b>Element Styling</b></label>
            <div class="field-option">
              <input
                type="checkbox"
                id="qr-transparent-bg"
                :checked="selection.item.transparentElementBg"
                @change="
                  $emit('update:selection-item-property', {
                    property: 'transparentElementBg',
                    value: $event.target.checked,
                  })
                "
              />
              <label for="qr-transparent-bg">Transparent background</label>
            </div>
          </div>

          <div class="setting" v-if="!selection.item.transparentElementBg">
            <label for="qr-bg-color">Background Color</label>
            <input
              type="color"
              id="qr-bg-color"
              :value="selection.item.backgroundColor"
              @input="
                $emit('update:selection-item-property', {
                  property: 'backgroundColor',
                  value: $event.target.value,
                })
              "
              class="color-picker"
            />
          </div>

          <div class="setting">
            <label for="qr-border-radius">Rounded Corners:</label>
            <input
              type="range"
              id="qr-border-radius"
              :value="selection.item.borderRadius"
              @input="
                $emit('update:selection-item-property', {
                  property: 'borderRadius',
                  value: $event.target.valueAsNumber,
                })
              "
              min="0"
              max="100"
            />
          </div>

          <div class="setting">
            <label for="qr-border-width">Border Width:</label>
            <input
              type="range"
              id="qr-border-width"
              :value="selection.item.borderWidth"
              @input="
                $emit('update:selection-item-property', {
                  property: 'borderWidth',
                  value: $event.target.valueAsNumber,
                })
              "
              min="0"
              max="20"
            />
          </div>

          <div class="setting" v-if="selection.item.borderWidth > 0">
            <label for="qr-border-color">Border Color</label>
            <input
              type="color"
              id="qr-border-color"
              :value="selection.item.borderColor"
              @input="
                $emit('update:selection-item-property', {
                  property: 'borderColor',
                  value: $event.target.value,
                })
              "
              class="color-picker"
            />
          </div>
        </div>
        <button
          class="sidebar-button remove-button"
          @click.stop="$emit('remove-element', selectedQrCode)"
        >
          Delete QR Code
        </button>
      </div>
    </div>

    <div
      v-if="weatherData"
      :class="{ active: selection.type === 'weather' }"
      class="element-box"
      @click="$emit('select-element', 'weather')"
    >
      <p>Weather</p>
      <div
        v-if="selection.type === 'weather'"
        @click.stop
        class="weather-options"
      >
        <div class="option-group">
          <div class="field-option">
            <input
              type="checkbox"
              id="weatherShowIcon"
              :checked="weatherElement.showIcon"
              @change="updateWeatherProperty($event, 'showIcon')"
            />
            <label for="weatherShowIcon">Show Icon</label>
          </div>
        </div>

        <div class="option-group">
          <label>Font Size:</label>
          <input
            type="range"
            :value="weatherElement.fontSize"
            @input="updateWeatherProperty($event, 'fontSize')"
            min="10"
            max="40"
            class="range-slider"
          />
        </div>

        <div class="option-group">
          <label>Text Color:</label>
          <input
            type="color"
            :value="weatherElement.textColor"
            @input="updateWeatherProperty($event, 'textColor')"
            class="color-picker"
          />
        </div>

        <div class="field-option">
          <input
            type="checkbox"
            id="weatherTransparentBg"
            :checked="weatherElement.transparentBg"
            @change="updateWeatherProperty($event, 'transparentBg')"
          />
          <label for="weatherTransparentBg">Transparent Background</label>
        </div>

        <div v-if="!weatherElement.transparentBg">
          <div class="option-group">
            <label>Background Color:</label>
            <input
              type="color"
              :value="weatherElement.backgroundColor"
              @input="updateWeatherProperty($event, 'backgroundColor')"
              class="color-picker"
            />
          </div>
          <div class="option-group">
            <label>Corner Radius:</label>
            <input
              type="range"
              :value="weatherElement.borderRadius"
              @input="updateWeatherProperty($event, 'borderRadius')"
              min="0"
              max="50"
              class="range-slider"
            />
          </div>
        </div>

        <button
          class="sidebar-button remove-button"
          @click.stop="$emit('remove-element', { id: 'weather' })"
        >
          Delete Weather
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { TILE_LAYERS } from "@/config/mapConfig.js";

export default {
  name: "EditorSidebar",
  props: {
    editorProductData: Object,
    activePlacement: String,
    selection: { type: Object, required: true },
    activityData: Object,
    availableGraphSources: Array,
    achievements: Array,
    activityPhotos: Array,
    mapSettings: Object,
    dataFields: Object,
    graphElements: Array,
    textBoxes: Array,
    photoElements: Array,
    badgeListElement: Object,
    qrCodeElements: Array,
    weatherElement: Object,
    weatherData: Object,
  },

  emits: [
    "select-element",
    "update:activePlacement",
    "update:mapSettings",
    "update:dataFields",
    "update:achievements",
    "update:graphElements",
    "update:textBoxes",
    "update:photoElements",
    "update:badgeListElement",
    "update:qrCodeElements",
    "update:weatherElement",
    "add-element",
    "remove-element",
    "hide-map",
    "reset-map",
    "hide-data-fields",
    "zoom-in",
    "zoom-out",
  ],

  data() {
    return {
      tileLayers: TILE_LAYERS,
      draggedField: null,
      dropTargetField: null,
      draggedBadge: null,
      dropTargetBadge: null,
      localCustomLink: "",
    };
  },

  computed: {
    isStravaActivity() {
      return this.activityData?.details?.source !== "gpx";
    },

    isCustomLinkValid() {
      if (!this.localCustomLink) return false;
      try {
        const url = new URL(this.localCustomLink);
        return url.protocol === "http:" || url.protocol === "https:";
      } catch (e) {
        return false;
      }
    },

    selectedGraph() {
      if (this.selection.type === "graph" && this.selection.item) {
        return this.graphElements.find((g) => g.id === this.selection.item.id);
      }
      return null;
    },

    selectedTextBox() {
      if (this.selection.type === "textBox" && this.selection.item) {
        return this.textBoxes.find((t) => t.id === this.selection.item.id);
      }
      return null;
    },

    selectedPhoto() {
      if (this.selection.type === "photo" && this.selection.item) {
        return this.photoElements.find((p) => p.id === this.selection.item.id);
      }
      return null;
    },

    selectedQrCode() {
      if (this.selection.type === "qrCode" && this.selection.item) {
        return this.qrCodeElements.find((q) => q.id === this.selection.item.id);
      }
      return null;
    },

    flatDataFields() {
      if (!this.dataFields || !this.dataFields.availableFields) return [];
      return [...this.dataFields.availableFields].sort(
        (a, b) => a.order - b.order
      );
    },

    sortedAchievements() {
      if (!this.achievements) return [];
      return [...this.achievements].sort((a, b) => a.order - b.order);
    },

    availableGradientOptions() {
      if (!this.activityData?.streams)
        return [{ value: "none", text: "Solid Color" }];
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
  },

  watch: {
    selectedQrCode: {
      handler(newQrCode) {
        if (newQrCode && newQrCode.linkType === "custom") {
          this.localCustomLink = newQrCode.customLink;
        } else if (newQrCode) {
          this.localCustomLink = "";
        }
      },
      immediate: true,
      deep: true,
    },
  },

  methods: {
    updateWeatherProperty(event, property) {
      const target = event.target;
      let value;

      if (target.type === "checkbox") {
        value = target.checked;
      } else {
        value = target.type === "range" ? target.valueAsNumber : target.value;
      }

      const updatedElement = { ...this.weatherElement, [property]: value };
      this.$emit("update:weatherElement", updatedElement);
    },

    updateMapSetting(key, value) {
      const newSettings = { ...this.mapSettings, [key]: value };
      this.$emit("update:mapSettings", newSettings);
    },

    zoomIn() {
      if (this.map) {
        this.map.zoomIn();
      }
    },

    zoomOut() {
      if (this.map) {
        this.map.zoomOut();
      }
    },

    handlePhotoUpload(event) {
      if (!this.selectedPhoto) {
        alert("Please select a photo element on the canvas first.");
        return;
      }
      const file = event.target.files[0];
      if (file) {
        if (!file.type.startsWith("image/")) {
          alert("Please select an image file.");
          return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
          this.updatePhotoProperty("src", e.target.result);
        };
        reader.readAsDataURL(file);
      }
      event.target.value = "";
    },

    updatePhotoProperty(property, value) {
      const updatedPhotos = this.photoElements.map((p) =>
        p.id === this.selectedPhoto.id ? { ...p, [property]: value } : p
      );
      this.$emit("update:photoElements", updatedPhotos);
    },

    updateCustomLink() {
      if (!this.isCustomLinkValid) return;
      this.updateQrCodeProperty("customLink", this.localCustomLink);
    },

    updateQrCodeProperty(property, value) {
      const updatedQRCodes = this.qrCodeElements.map((q) =>
        q.id === this.selectedQrCode.id ? { ...q, [property]: value } : q
      );
      this.$emit("update:qrCodeElements", updatedQRCodes);
    },

    updateTextBoxProperty(property, value) {
      const updatedTextBoxes = this.textBoxes.map((t) =>
        t.id === this.selectedTextBox.id ? { ...t, [property]: value } : t
      );
      this.$emit("update:textBoxes", updatedTextBoxes);
    },

    updateGraphProperty(property, value) {
      const updatedGraphs = this.graphElements.map((g) => {
        if (g.id === this.selectedGraph.id) {
          const updatedGraph = { ...g, [property]: value };
          if (property === "selectedDataSource") {
            updatedGraph.yAxisMin = null;
            updatedGraph.yAxisMax = null;
          }
          return updatedGraph;
        }
        return g;
      });
      this.$emit("update:graphElements", updatedGraphs);
    },

    selectElement(type, item = null) {
      this.$emit("select-element", type, item);
    },

    updateArrayItem(collectionName, item, property, value) {
      const collection = this[collectionName];
      const updatedCollection = collection.map((i) =>
        i.id === item.id ? { ...i, [property]: value } : i
      );
      this.$emit(`update:${collectionName}`, updatedCollection);
    },

    toggleDataField(field, isSelected) {
      const updatedFields = this.dataFields.availableFields.map((f) =>
        f.id === field.id ? { ...f, selected: isSelected } : f
      );
      this.$emit("update:dataFields", {
        ...this.dataFields,
        availableFields: updatedFields,
      });
    },

    handleDragStart(event, field) {
      this.draggedField = field;
      event.dataTransfer.effectAllowed = "move";
    },

    handleDragOver(event, targetField) {
      if (!this.draggedField || this.draggedField.id === targetField.id) return;
      this.dropTargetField = targetField;
    },

    handleDrop() {
      if (!this.draggedField || !this.dropTargetField) return;

      const fields = [...this.flatDataFields];
      const draggedIndex = fields.findIndex(
        (f) => f.id === this.draggedField.id
      );
      const targetIndex = fields.findIndex(
        (f) => f.id === this.dropTargetField.id
      );

      const [draggedItem] = fields.splice(draggedIndex, 1);
      fields.splice(targetIndex, 0, draggedItem);

      const newOrderMap = new Map(fields.map((f, index) => [f.id, index]));
      const updatedAvailableFields = this.dataFields.availableFields.map(
        (f) => ({
          ...f,
          order: newOrderMap.get(f.id),
        })
      );

      this.$emit("update:dataFields", {
        ...this.dataFields,
        availableFields: updatedAvailableFields,
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

    handleBadgeDragStart(event, badge) {
      event.dataTransfer.setData("text/plain", badge.id);
      event.dataTransfer.effectAllowed = "move";
    },

    handleBadgeDragOver(event, targetBadge) {
      const draggedId = event.dataTransfer.getData("text/plain");
      if (!draggedId || draggedId === targetBadge.id) return;
      this.dropTargetBadge = targetBadge;
    },

    handleBadgeDrop(event, targetBadge) {
      event.preventDefault();

      const draggedId = event.dataTransfer.getData("text/plain");

      if (!draggedId || !targetBadge) {
        this.handleBadgeDragEnd();
        return;
      }

      const reorderedAchievements = [...this.sortedAchievements];
      const draggedIndex = reorderedAchievements.findIndex(
        (a) => a.id === draggedId
      );
      const targetIndex = reorderedAchievements.findIndex(
        (a) => a.id === targetBadge.id
      );

      if (draggedIndex === -1 || targetIndex === -1) {
        this.handleBadgeDragEnd();
        return;
      }

      const [draggedItem] = reorderedAchievements.splice(draggedIndex, 1);
      reorderedAchievements.splice(targetIndex, 0, draggedItem);

      const finalAchievements = reorderedAchievements.map((ach, index) => ({
        ...ach,
        order: index,
      }));

      this.$emit("update:achievements", finalAchievements);
      this.handleBadgeDragEnd();
    },

    handleBadgeDragEnd() {
      this.dropTargetBadge = null;
    },

    toggleAchievement(achievement, isSelected) {
      const updatedAchievements = this.achievements.map((a) =>
        a.id === achievement.id ? { ...a, selected: isSelected } : a
      );
      this.$emit("update:achievements", updatedAchievements);
    },
  },
};
</script>

<style scoped>
.placement-controls-wrapper {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.placement-controls {
  display: flex;
  gap: 10px;
  background-color: #f0f2f5;
  padding: 5px;
  border-radius: 8px;
}

.placement-controls button {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid #ccc;
  background-color: #fff;
  cursor: pointer;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.2s ease;
  text-transform: capitalize;
}

.placement-controls button:hover {
  background-color: #e9e9e9;
  border-color: #aaa;
}

.placement-controls button.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.custom-link-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
}

.custom-link-wrapper input {
  flex-grow: 1;
  margin-bottom: 0;
}

.custom-link-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
}

.custom-link-wrapper input {
  flex-grow: 1;
  margin-bottom: 0;
}

.link-validate-btn {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border: 1px solid #ccc;
  border-radius: 5px;
  color: white;
  font-size: 1.2em;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: background-color 0.2s, opacity 0.2s;
  background-color: #e9ecef;
  cursor: not-allowed;
  opacity: 0.6;
}

.link-validate-btn.is-valid {
  background-color: #28a745;
  cursor: pointer;
  opacity: 1;
}

.link-validate-btn.is-valid:hover {
  background-color: #218838;
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

h2 {
  margin-top: 0;
  color: #333;
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
.data-fields-options,
.weather-options {
  text-align: left;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
  cursor: default;
}

label {
  display: block;
  font-size: 0.9em;
  margin-bottom: 5px;
  color: #555;
}

select,
input[type="range"],
input[type="color"] {
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 10px;
}

.color-picker {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-color: transparent;
  border: 1px solid #ccc;
  cursor: pointer;
  height: 35px;
  padding: 0;
  border-radius: 5px;
}

.color-picker::-webkit-color-swatch {
  border: none;
  border-radius: 4px;
}

.range-slider {
  vertical-align: middle;
}

.field-option {
  margin-top: 10px;
  display: flex;
  align-items: center;
  position: relative;
  padding: 4px 0;
}

.field-option label {
  margin: 0 0 0 8px;
  flex-grow: 1;
}

.field-option input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.zoom-controls {
  margin-top: 15px;
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
  background-color: #4287f5;
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
  flex-grow: 1;
  margin: 0 !important;
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

.upload-button {
  background-color: #007bff;
}

.upload-button:hover {
  background-color: #0056b3;
}

label.sidebar-button {
  display: block;
  text-align: center;
  padding: 8px 15px;
}

.pan-controls {
  margin-top: 15px;
}

.pan-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
  width: 120px;
  margin-top: 5px;
}

.pan-button {
  width: 35px;
  height: 35px;
  border: 1px solid #ccc;
  background-color: #f0f0f0;
  color: #333;
  cursor: pointer;
  font-size: 1.5em;
  font-weight: bold;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.pan-button:hover {
  background-color: #e0e0e0;
  border-color: #bbb;
}

.pan-button.center-button {
  background-color: #e0e0e0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px #888;
  align-self: center;
  justify-self: center;
}
</style>
