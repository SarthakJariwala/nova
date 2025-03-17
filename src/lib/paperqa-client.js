import { invoke } from "@tauri-apps/api/core";

export class PaperQAClient {
	connected = false;

	async connect() {
		if (!this.connected) {
			try {
				await invoke("connect_to_zmq_server");
				this.connected = true;
				console.log("Connected to PaperQA server");
			} catch (error) {
				console.error("Failed to connect to PaperQA server:", error);
				throw error;
			}
		}
	}

	async sendRequest(method, params = {}) {
		if (!this.connected) {
			await this.connect();
		}

		try {
			const response = await invoke("send_zmq_request", {
				method,
				params: JSON.stringify(params),
			});

			return JSON.parse(response);
		} catch (error) {
			console.error(`Error sending ${method} request:`, error);
			throw error;
		}
	}

	async initialize(paperDir, options = {}) {
		const params = {
			paper_dir: paperDir,
			...options,
		};
		return await this.sendRequest("initialize", params);
	}

	async ask(question) {
		return await this.sendRequest("ask", { question });
	}

	async updateSettings(settings) {
		return await this.sendRequest("update_settings", settings);
	}

	async getPresetNames() {
		return await this.sendRequest("get_preset_names");
	}

	async getStatus() {
		return await this.sendRequest("get_status");
	}

	async close() {
		if (this.connected) {
			try {
				await invoke("disconnect_from_zmq_server");
				this.connected = false;
				console.log("Disconnected from PaperQA server");
			} catch (error) {
				console.error("Error disconnecting from server:", error);
				throw error;
			}
		}
	}
}

// Create a singleton instance
const paperQAClient = new PaperQAClient();
export default paperQAClient;
