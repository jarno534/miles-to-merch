import { reactive } from "vue";

export const settings = reactive({
  units: "metric",

  setUnits(newUnits) {
    if (newUnits === "metric" || newUnits === "imperial") {
      this.units = newUnits;
      localStorage.setItem("user-units", newUnits);
    }
  },

  loadSettings() {
    const savedUnits = localStorage.getItem("user-units");
    if (savedUnits) {
      this.units = savedUnits;
    }
  },
});

settings.loadSettings();
