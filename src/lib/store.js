import { load } from "@tauri-apps/plugin-store";

const defaultSettings = {
  llm: "gpt-4o-2024-11-20",
  summary_llm: "gpt-4o-2024-11-20",
  agent_llm: "gpt-4o-2024-11-20",
  embedding: "text-embedding-3-small",
  temperature: 0.0,
  evidence_k: 10,
  max_sources: 5,
  chunk_size: 5000,
  use_tier1_limits: true,
  preset: "high_quality",
  paper_dir: "",
  api_key: "",
};

let store;

async function initStore() {
  store = await load("settings.json", { autoSave: true });
  return store;
}

// Load settings from the store
export async function loadSettings() {
  store = await initStore();
  const storedSettings = await store.get("userSettings");
  return { ...defaultSettings, ...storedSettings };
}

// Save settings to the store
export async function saveSettings(settings) {
  store = await initStore();
  await store.set("userSettings", settings);
  return { success: true };
}
