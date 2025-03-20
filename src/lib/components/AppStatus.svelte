<script>
    import paperQAClient from "$lib/paperqa-client";
    import { Badge } from "$lib/components/ui/badge/index";

    let status = $state(null);
    let error = $state("");
    let isLoading = $state(true);

    $effect(() => {
        checkStatus();
    });

    async function checkStatus() {
        isLoading = true;
        error = "";

        try {
            const result = await paperQAClient.getStatus();
            status = result;
        } catch (err) {
            console.error("Error checking status:", err);
            error = `Error checking status: ${err.message}`;
        } finally {
            isLoading = false;
        }
    }

    // Expose a method to manually refresh the status
    // This can be called from other components
    function refreshStatus() {
        return checkStatus();
    }

    // Make the refreshStatus function globally available so other components can call it
    if (typeof window !== "undefined") {
        window.refreshPaperQAStatus = refreshStatus;
    }
</script>

<div class="border rounded p-4">
    <h2 class="text-lg font-semibold mb-2">Status</h2>

    {#if isLoading}
        <Badge variant="secondary">Loading...</Badge>
    {:else if error}
        <Badge variant="destructive">{error}</Badge>
    {:else if status}
        <div class="space-y-2">
            <Badge
                variant={status.status === "initialized"
                    ? "default"
                    : "outline"}
            >
                {status.status === "initialized" ? "Ready" : "Not Initialized"}
            </Badge>

            {#if status.status === "initialized"}
                <div class="flex justify-between border-b pb-2">
                    <span class="font-medium">Paper Directory:</span>
                    <span class="text-sm">{status.paper_dir}</span>
                </div>

                <div class="flex justify-between border-b pb-2">
                    <span class="font-medium">LLM:</span>
                    <span class="text-sm">{status.llm}</span>
                </div>

                <div class="flex justify-between border-b pb-2">
                    <span class="font-medium">Embedding:</span>
                    <span class="text-sm">{status.embedding}</span>
                </div>

                <div class="flex justify-between pb-2">
                    <span class="font-medium">Preset:</span>
                    <span class="text-sm">{status.preset}</span>
                </div>
            {/if}
        </div>
    {:else}
        <div class="py-2">No status information available</div>
    {/if}
</div>
