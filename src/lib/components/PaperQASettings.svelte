<script>
    import { Button } from "@/components/ui/button";
    import { Checkbox } from "@/components/ui/checkbox";
    import { Input } from "@/components/ui/input";
    import { Label } from "@/components/ui/label";
    import * as Select from "@/components/ui/select/index.js";
    import paperQAClient from "@/paperqa-client";
    import { getUserSettings } from "@/store.svelte";

    const store = getUserSettings();

    /**
     * @type {string[]}
     */
    let presets = $state([]);
    let isLoading = $state(false);
    let error = $state("");
    let success = $state("");
    let showApiKey = $state(false);

    $effect(() => {
        loadPresets();
    });

    async function loadPresets() {
        try {
            const result = await paperQAClient.getPresetNames();
            if (result.status === "success") {
                presets = result.presets || [];
            }
        } catch (err) {
            console.error("Error loading presets:", err);
        }
    }

    async function updateSettings() {
        error = "";
        success = "";
        isLoading = true;

        try {
            const result = await paperQAClient.updateSettings(store.settings);
            if (result.status === "success") {
                // Update settings in store
                store.saveSettings()
                success = "Settings updated successfully";
                // Refresh status after updating settings
                if (
                    typeof window !== "undefined" &&
                    window.refreshPaperQAStatus
                ) {
                    window.refreshPaperQAStatus();
                }
            } else {
                error = result.message || "Failed to update settings";
            }
        } catch (err) {
            console.error("Error updating settings:", err);
            error = `Error updating settings: ${err.message}`;
        } finally {
            isLoading = false;
        }
    }

    function toggleApiKeyVisibility() {
        showApiKey = !showApiKey;
    }
</script>

<div class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-2 md:col-span-2">
            <Label>API Key</Label>
            <div class="flex gap-2">
                <Input
                    type={showApiKey ? "text" : "password"}
                    bind:value={store.settings.api_key}
                    placeholder="sk-..."
                />
                <Button
                    variant="outline"
                    type="button"
                    onclick={toggleApiKeyVisibility}
                >
                    {showApiKey ? "Hide" : "Show"}
                </Button>
            </div>
            <p class="text-xs text-muted-foreground">
                Your API key is only stored locally and sent only to LLM
                providers.
            </p>
        </div>
        <div class="space-y-2">
            <Label>LLM Model</Label>
            <Input type="text" bind:value={store.settings.llm} />
        </div>

        <div class="space-y-2">
            <Label>Summary LLM</Label>
            <Input type="text" bind:value={store.settings.summary_llm} />
        </div>

        <div class="space-y-2">
            <Label>Agent LLM</Label>
            <Input type="text" bind:value={store.settings.agent_llm} />
        </div>

        <div class="space-y-2">
            <Label>Embedding Model</Label>
            <Input type="text" bind:value={store.settings.embedding} />
        </div>

        <div class="space-y-2">
            <Label>Temperature</Label>
            <Input
                type="number"
                min="0"
                max="1"
                step="0.1"
                bind:value={store.settings.temperature}
            />
        </div>

        <div class="space-y-2">
            <Label>Evidence K</Label>
            <Input type="number" min="1" bind:value={store.settings.evidence_k} />
        </div>

        <div class="space-y-2">
            <Label>Max Sources</Label>
            <Input type="number" min="1" bind:value={store.settings.max_sources} />
        </div>

        <div class="space-y-2">
            <Label>Chunk Size</Label>
            <Input type="number" min="100" bind:value={store.settings.chunk_size} />
        </div>

        <div class="space-y-2">
            <Label>Preset</Label>
            <Select.Root type="single" bind:value={store.settings.preset}>
                <Select.Trigger class="w-full">
                    {store.settings.preset || "Select a preset"}
                </Select.Trigger>
                <Select.Content>
                    <Select.Item value="">None</Select.Item>
                    {#each presets as preset}
                        <Select.Item value={preset} label={preset}
                            >{preset}</Select.Item
                        >
                    {/each}
                </Select.Content>
            </Select.Root>
        </div>

        <div class="space-y-2">
            <Label>Use Tier 1 Rate Limits</Label>
            <div>
                <Checkbox bind:checked={store.settings.use_tier1_limits} />
            </div>
        </div>
    </div>

    <Button onclick={updateSettings} disabled={isLoading} variant="default">
        {isLoading ? "Updating..." : "Update Settings"}
    </Button>

    {#if error}
        <div
            class="p-3 bg-destructive/20 text-destructive border border-destructive rounded"
        >
            {error}
        </div>
    {/if}

    {#if success}
        <div
            class="p-3 bg-green-100 text-green-800 border border-green-200 rounded"
        >
            {success}
        </div>
    {/if}
</div>
