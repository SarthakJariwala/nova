<script>
    import { open } from "@tauri-apps/plugin-dialog";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import paperQAClient from "$lib/paperqa-client";
    import { loadSettings, saveSettings } from "@/store";

    let paperDir = $state("");
    let isLoading = $state(false);
    let error = $state("");

    $effect(() => {
        loadSettings().then((settings) => {
            if (settings.paper_dir) {
                paperDir = settings.paper_dir;
            }
        });
    });

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
    async function initializePaperQA(event) {
        event.preventDefault();
        if (!paperDir) {
            error = "Please select a papers directory first";
            return;
        }

        error = "";
        isLoading = true;

        try {
            const result = await paperQAClient.initialize(paperDir);
            if (result.status === "success") {
                console.log("PaperQA initialized successfully");
                // Refresh status after initialization
                if (
                    typeof window !== "undefined" &&
                    window.refreshPaperQAStatus
                ) {
                    window.refreshPaperQAStatus();
                }
            } else {
                error = result.message || "Failed to initialize PaperQA";
            }
        } catch (err) {
            console.error("Error initializing PaperQA:", err);
            error = `Error initializing PaperQA: ${err.message}`;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="space-y-4">
    <h2 class="text-lg font-semibold">Paper Directory</h2>

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
            onclick={initializePaperQA}
            disabled={isLoading}
            variant="default"
        >
            {isLoading ? "Initializing..." : "Initialize PaperQA"}
        </Button>
    {/if}

    {#if error}
        <div
            class="p-3 bg-destructive/20 text-destructive border border-destructive rounded"
        >
            {error}
        </div>
    {/if}
</div>
