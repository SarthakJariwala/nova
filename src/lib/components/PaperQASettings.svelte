<script>
    import { Button } from "$lib/components/ui/button";
    import { Checkbox } from "$lib/components/ui/checkbox";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import paperQAClient from "$lib/paperqa-client";

    let settings = $state({
        llm: "gpt-4o-2024-11-20",
        summary_llm: "gpt-4o-2024-11-20",
        agent_llm: "gpt-4o-2024-11-20",
        embedding: "text-embedding-3-small",
        temperature: 0.0,
        evidence_k: 10,
        max_sources: 5,
        chunk_size: 5000,
        use_tier1_limits: true,
        preset: "",
    });

    let presets = $state([]);
    let isLoading = $state(false);
    let error = $state("");
    let success = $state("");

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

    async function updateSettings(event) {
        event.preventDefault();
        error = "";
        success = "";
        isLoading = true;

        try {
            const result = await paperQAClient.updateSettings(settings);
            if (result.status === "success") {
                success = "Settings updated successfully";
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
</script>

<div class="space-y-6">
    <h2 class="text-lg font-semibold">PaperQA Settings</h2>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-2">
            <Label>LLM Model</Label>
            <Input
                type="text"
                class="w-full p-2 border rounded"
                bind:value={settings.llm}
            />
        </div>

        <div class="space-y-2">
            <Label>Summary LLM</Label>
            <Input
                type="text"
                class="w-full p-2 border rounded"
                bind:value={settings.summary_llm}
            />
        </div>

        <div class="space-y-2">
            <Label>Agent LLM</Label>
            <Input
                type="text"
                class="w-full p-2 border rounded"
                bind:value={settings.agent_llm}
            />
        </div>

        <div class="space-y-2">
            <Label>Embedding Model</Label>
            <Input
                type="text"
                class="w-full p-2 border rounded"
                bind:value={settings.embedding}
            />
        </div>

        <div class="space-y-2">
            <Label>Temperature</Label>
            <Input
                type="number"
                min="0"
                max="1"
                step="0.1"
                class="w-full p-2 border rounded"
                bind:value={settings.temperature}
            />
        </div>

        <div class="space-y-2">
            <Label>Evidence K</Label>
            <Input
                type="number"
                min="1"
                class="w-full p-2 border rounded"
                bind:value={settings.evidence_k}
            />
        </div>

        <div class="space-y-2">
            <Label>Max Sources</Label>
            <Input
                type="number"
                min="1"
                class="w-full p-2 border rounded"
                bind:value={settings.max_sources}
            />
        </div>

        <div class="space-y-2">
            <Label>Chunk Size</Label>
            <Input
                type="number"
                min="100"
                class="w-full p-2 border rounded"
                bind:value={settings.chunk_size}
            />
        </div>

        <div class="space-y-2">
            <Label>Preset</Label>
            <select
                class="w-full p-2 border rounded"
                bind:value={settings.preset}
            >
                <option value="">None</option>
                {#each presets as preset}
                    <option value={preset}>{preset}</option>
                {/each}
            </select>
        </div>

        <div class="space-y-2">
            <Label>Use Tier 1 Rate Limits</Label>
            <Checkbox bind:checked={settings.use_tier1_limits} />
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
