import { settings } from "@/settings";

export function formatEffortTime(seconds) {
  return new Date(seconds * 1000).toISOString().substr(11, 8);
}

export function formatDistance(m) {
  if (m === undefined) return "-";
  if (settings.units === "imperial") {
    const miles = m * 0.000621371;
    return `${miles.toFixed(2)} mi`;
  }
  return `${(m / 1000).toFixed(2)} km`;
}

export function formatTime(s) {
  return s === undefined ? "-" : new Date(s * 1000).toISOString().substr(11, 8);
}

export function formatPace(sPerKm) {
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
}

export function formatSpeed(mps) {
  if (mps === undefined) return "-";
  if (settings.units === "imperial") {
    const mph = mps * 2.23694;
    return `${mph.toFixed(1)} mph`;
  }
  return `${(mps * 3.6).toFixed(1)} km/h`;
}

export function formatElevation(m) {
  if (m === undefined) return "-";
  if (settings.units === "imperial") {
    const feet = m * 3.28084;
    return `${Math.round(feet)} ft`;
  }
  return `${Math.round(m)} m`;
}

export function formatHeartRate(bpm) {
  return bpm === undefined ? "-" : `${Math.round(bpm)} bpm`;
}

export function formatCadence(spm) {
  return spm === undefined ? "-" : `${Math.round(spm)} spm`;
}

export function formatPower(w) {
  return w === undefined ? "-" : `${Math.round(w)} W`;
}

export function getOrdinal(n) {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}
