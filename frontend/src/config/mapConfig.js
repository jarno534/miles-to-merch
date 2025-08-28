export const TILE_LAYERS = {
  "3d-terrain": {
    name: "3D Terrain",
    is3D: true,
    url: `https://api.maptiler.com/maps/outdoor-v2/style.json?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>',
  },
  streets: {
    name: "Streets",
    url: `https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>',
  },
  satellite: {
    name: "Satellite",
    url: `https://api.maptiler.com/maps/satellite/{z}/{x}/{y}.jpg?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a>',
  },
  topo: {
    name: "Topo",
    url: `https://api.maptiler.com/maps/topo-v2/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>',
  },
  outdoor: {
    name: "Outdoor",
    url: `https://api.maptiler.com/maps/outdoor-v2/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>',
  },
  winter: {
    name: "Winter",
    url: `https://api.maptiler.com/maps/winter-v2/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>',
  },
  ocean: {
    name: "Ocean",
    url: `https://api.maptiler.com/maps/ocean/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a>',
  },
  basic: {
    name: "Basic",
    url: `https://api.maptiler.com/maps/basic-v2/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>',
  },
  bright: {
    name: "Bright",
    url: `https://api.maptiler.com/maps/bright-v2/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>',
  },
  dataviz: {
    name: "Dataviz",
    url: `https://api.maptiler.com/maps/dataviz/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a>',
  },
  toner: {
    name: "Toner (Zwart/Wit)",
    url: `https://api.maptiler.com/maps/toner-v2/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>',
  },
  backdrop: {
    name: "Backdrop",
    url: `https://api.maptiler.com/maps/backdrop/{z}/{x}/{y}.png?key=${process.env.VUE_APP_MAPTILER_API_KEY}`,
    attribution:
      '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a>',
  },
  aquarelle: {
    name: "Aquarelle (Watercolor)",
    // LET OP: Deze gebruikt een andere provider en vereist een VUE_APP_STADIA_API_KEY
    url: `https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg?api_key=${process.env.VUE_APP_STADIA_API_KEY}`,
    attribution:
      '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://stamen.com/" target="_blank">Stamen Design</a>',
  },
  openstreetmap: {
    name: "OpenStreetMap",
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
};
