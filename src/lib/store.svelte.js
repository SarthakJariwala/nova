import { load } from "@tauri-apps/plugin-store";
import { getContext, setContext } from "svelte";

const defaultSettings = {
  llm: "gemini/gemini-2.0-flash",
  summary_llm: "gemini/gemini-2.0-flash",
  agent_llm: "gemini/gemini-2.0-flash",
  embedding: "gemini/text-embedding-004",
  temperature: 0.0,
  evidence_k: 10,
  max_sources: 5,
  chunk_size: 5000,
  use_tier1_limits: true,
  preset: "fast",
  paper_dir: "",
  api_key: "",
};

export class UserSettingsStore {
  settings = $state({
    ...defaultSettings,
  });

  constructor() {
    this.initializeStore();
  }

  async initializeStore() {
    try {
      this.store = await load("settings.json", { autoSave: true });
      const storedSettings = await this.store.get("userSettings");
      this.settings = { ...defaultSettings, ...storedSettings };
    } catch (error) {
      console.error("Failed to initialize store:", error);
    }
  }

  async saveSettings() {
    try {
      if (this.store) {
        await this.store.set("userSettings", this.settings);
      }
    } catch (error) {
      console.error("Failed to save settings:", error);
    }
  }
}

const USER_SETTINGS_KEY = "userSettings";

export function setUserSettings() {
  return setContext(USER_SETTINGS_KEY, new UserSettingsStore());
}

export function getUserSettings() {
  return getContext(USER_SETTINGS_KEY);
}

const defaultHistory = [{}];

export class HistoryStore {
  history = $state(defaultHistory);
  
  constructor() {
    this.initializeStore();
  }
  
  async initializeStore() {
    try {
      this.store = await load("history.json", { autoSave: true });
      const storedHistory = await this.store.get("qaHistory");
      if (storedHistory) {
        this.history = storedHistory;
      }
    } catch (error) {
      console.error("Failed to initialize history store:", error);
    }
  }
  
  async addEntry(entry) {
    // Add timestamp to entry
    const entryWithTimestamp = {
      ...entry,
      timestamp: new Date().toISOString()
    };
    
    // Add to the beginning of the array to show newest first
    this.history = [entryWithTimestamp, ...this.history];
    
    // Save to persistent storage
    await this.saveHistory();
  }
  
  async deleteEntry(index) {
    this.history = this.history.filter((_, i) => i !== index);
    await this.saveHistory();
  }
  
  async clearHistory() {
    this.history = [];
    await this.saveHistory();
  }
  
  async saveHistory() {
    try {
      if (this.store) {
        await this.store.set("qaHistory", this.history);
      }
    } catch (error) {
      console.error("Failed to save history:", error);
    }
  }
}

const HISTORY_KEY = "qaHistory";

export function setHistoryStore() {
  return setContext(HISTORY_KEY, new HistoryStore());
}

export function getHistoryStore() {
  return getContext(HISTORY_KEY);
} 