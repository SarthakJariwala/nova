<script>
    import { open } from "@tauri-apps/plugin-dialog";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import paperQAClient from "$lib/paperqa-client";
    import { loadSettings, saveSettings } from "@/store";
    import { onMount } from "svelte";

    let paperDir = $state("");
    let isLoading = $state(false);
    let error = $state("");
    let apiKeyConfigured = $state(false);
    let settings = $state({});

    onMount(async () => {
        settings = await loadSettings();
        // if there is a paper directory configured,
        // we want to initialize Nova right away
        if (settings.paper_dir) {
            paperDir = settings.paper_dir;
            await initializeNova();
        }

        if (settings.api_key) {
            await paperQAClient.updateSettings({ ...settings });
            await checkApiKeyStatus();
        }
    });

    async function checkApiKeyStatus() {
        try {
            const status = await paperQAClient.getStatus();
            apiKeyConfigured = Boolean(status.api_key_configured);
        } catch (err) {
            console.error("Error checking API key status:", err);
        }
    }

    /**
     * @param {{ preventDefault: () => void; }} event
     */
    async function selectDirectory(event) {
        event.preventDefault();
        try {
            const selected = await open({
                directory: true,
                multiple: false,
                title: "Select a folder with your papers",
            });

            if (selected && typeof selected === "string") {
                paperDir = selected;
                saveSettings({ paper_dir: selected });
            }
        } catch (err) {
            console.error("Error selecting directory:", err);
            error = `Error selecting directory: ${err.message}`;
        }
    }

    async function initializeNova() {
        if (!paperDir) {
            error = "Please select a papers directory first";
            return;
        }

        error = "";
        isLoading = true;

        try {
            const result = await paperQAClient.initialize(paperDir, {
                preset: settings.preset,
                llm: settings.llm,
                summary_llm: settings.summary_llm,
                agent_llm: settings.agent_llm,
                embedding: settings.embedding,
                temperature: settings.temperature,
                evidence_k: settings.evidence_k,
                max_sources: settings.max_sources,
                chunk_size: settings.chunk_size,
                use_tier1_limits: settings.use_tier1_limits,
            });
            if (result.status === "success") {
                console.log("Nova initialized successfully");
                // Refresh status after initialization
                if (
                    typeof window !== "undefined" &&
                    window.refreshPaperQAStatus
                ) {
                    window.refreshPaperQAStatus();
                }
            } else {
                error = result.message || "Failed to initialize Nova";
            }
        } catch (err) {
            console.error("Error initializing Nova:", err);
            error = `Error initializing Nova: ${err.message}`;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="space-y-4">
    <div class="flex gap-2 items-center">
        <Input
            type="text"
            placeholder="Select papers directory"
            value={paperDir}
            readonly
        />
        <Button onclick={selectDirectory}>Browse</Button>
    </div>

    {#if paperDir}
        <Button onclick={initializeNova} disabled={isLoading} variant="default">
            {isLoading ? "Initializing..." : "Initialize Nova"}
        </Button>

        {#if !apiKeyConfigured}
            <div class="text-sm text-destructive">
                API key not configured. Please go to Settings to add your API
                key.
            </div>
        {/if}
    {/if}

    {#if error}
        <div
            class="p-3 bg-destructive/20 text-destructive border border-destructive rounded"
        >
            {error}
        </div>
    {/if}
</div>
