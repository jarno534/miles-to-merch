<template>
  <transition name="modal-fade">
    <div v-if="visible" class="modal-backdrop">
      <div class="modal-content">
        <h2 class="modal-title">Choose Your Units</h2>
        <p class="modal-message">
          Select the unit system you'd like to see for distance, temperature,
          and elevation.
        </p>
        <div class="modal-actions">
          <button @click="selectUnits('metric')" class="button-primary">
            Metric (km, °C)
          </button>
          <button @click="selectUnits('imperial')" class="button-primary">
            Imperial (miles, °F)
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: "UnitsModal",
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["units-selected"], // Declare the event
  methods: {
    selectUnits(units) {
      // Send the chosen unit system back to the parent component
      this.$emit("units-selected", units);
    },
  },
};
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000; /* Zorg ervoor dat het boven alles staat */
}
.modal-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
  text-align: center;
}
.modal-title {
  margin-top: 0;
  font-size: 1.8rem;
  color: #333;
}
.modal-message {
  margin-bottom: 25px;
  line-height: 1.6;
  color: #555;
  font-size: 1.1rem;
}
.modal-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}
.button-primary {
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  background-color: #fc4c02;
  color: white;
  font-size: 1rem;
  transition: background-color 0.2s;
}
.button-primary:hover {
  background-color: #e24300;
}
</style>
