<script>
    import paperQAClient from "$lib/paperqa-client";

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
</script>

<div class="border rounded p-4">
    <h2 class="text-lg font-semibold mb-4">System Status</h2>

    {#if isLoading}
        <div class="py-2">Loading status...</div>
    {:else if error}
        <div
            class="p-3 bg-destructive/20 text-destructive border border-destructive rounded"
        >
            {error}
        </div>
    {:else if status}
        <div class="space-y-2">
            <div class="flex justify-between border-b pb-2">
                <span class="font-medium">Status:</span>
                <span
                    class="px-2 py-0.5 rounded text-xs {status.status ===
                    'initialized'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'}"
                >
                    {status.status === "initialized"
                        ? "Ready"
                        : "Not Initialized"}
                </span>
            </div>

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
