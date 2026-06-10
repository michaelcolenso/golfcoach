// Shared analysis state, persisted to sessionStorage so a refresh on
// /results doesn't lose the report.

const STORAGE_KEY = "golfcoach:analysis";

function load() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

class AnalysisState {
  result = $state(load());

  set(result) {
    this.result = result;
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(result));
    } catch {
      // Quota exceeded (base64 frames can be large) — keep in-memory state only.
    }
  }

  clear() {
    this.result = null;
    sessionStorage.removeItem(STORAGE_KEY);
  }
}

export const analysis = new AnalysisState();
