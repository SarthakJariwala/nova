<script>
    import { open } from "@tauri-apps/plugin-dialog";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import paperQAClient from "$lib/paperqa-client";
    import { loadSettings, saveSettings } from "@/store";

    let paperDir = $state("");
    let isLoading = $state(false);
    let error = $state("");
    let apiKeyConfigured = $state(false);

    $effect(() => {
        loadSettings().then((settings) => {
            if (settings.paper_dir) {
                paperDir = settings.paper_dir;
            }
            // Check if API key is configured
            apiKeyConfigured = Boolean(settings.openai_api_key);
        });

        // Also check API key status when the component loads
        checkApiKeyStatus();
    });

    async function checkApiKeyStatus() {
        try {
            const status = await paperQAClient.getStatus();
            apiKeyConfigured = status.api_key_configured;
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
                title: "Select Papers Directory",
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

    /**
     * @param {{ preventDefault: () => void; }} event
     */
    async function initializeNova(event) {
        event.preventDefault();
        if (!paperDir) {
            error = "Please select a papers directory first";
            return;
        }

        if (!apiKeyConfigured) {
            error = "Please configure your API key in Settings first";
            return;
        }

        error = "";
        isLoading = true;

        try {
            const result = await paperQAClient.initialize(paperDir);
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
        <Button
            onclick={initializeNova}
            disabled={isLoading || !apiKeyConfigured}
            variant="default"
        >
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
