<script>
    import paperQAClient from "$lib/paperqa-client";
    import { Badge } from "$lib/components/ui/badge/index";
    import * as Card from "$lib/components/ui/card/index";

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
            status = await paperQAClient.getStatus();
        } catch (err) {
            console.error("Error checking status:", err);
            error = `Error checking status: ${err.message}`;
        } finally {
            isLoading = false;
        }
    }

    // Expose a method to manually refresh the status
    // This can be called from other components
    async function refreshStatus() {
        await checkStatus();
    }

    // Make the refreshStatus function globally available so other components can call it
    if (typeof window !== "undefined") {
        window.refreshPaperQAStatus = refreshStatus;
    }
</script>

<Card.Root>
    <Card.Header
        class="flex flex-row items-center justify-between space-y-0 pb-2"
    >
        <Card.Title>Status</Card.Title>
        {#if isLoading}
            <div class="flex items-center justify-center py-4">
                <Badge variant="secondary">Loading...</Badge>
            </div>
        {:else if error}
            <div class="py-2">
                <Badge variant="destructive">{error}</Badge>
            </div>
        {:else if status}
            <div class="space-y-3">
                <div class="flex justify-between items-center">
                    <Badge
                        variant={status.status === "initialized"
                            ? "default"
                            : "outline"}
                    >
                        {status.status === "initialized"
                            ? "Ready"
                            : "Not Initialized"}
                    </Badge>
                </div>
            </div>
        {/if}
    </Card.Header>

    <Card.Content>
        <div class="space-y-3">
            {#if status}
                {#if !status.api_key_configured}
                    <div class="py-2">
                        <Badge variant="destructive">API Key Missing</Badge>
                        <p class="text-xs text-muted-foreground mt-1">
                            Configure your API key in Settings
                        </p>
                    </div>
                {:else}
                    <div class="py-2">
                        <Badge variant="secondary">API Key Configured</Badge>
                    </div>
                {/if}

                {#if status.status === "initialized"}
                    <div class="space-y-3 pt-2 pb-2">
                        <div class="flex flex-col space-y-1">
                            <p class="text-sm font-medium">Paper Directory</p>
                            <p class="text-xs text-muted-foreground">
                                {status.paper_dir}
                            </p>
                        </div>

                        <div class="flex flex-col space-y-1">
                            <p class="text-sm font-medium">LLM</p>
                            <p class="text-xs text-muted-foreground">
                                {status.llm}
                            </p>
                        </div>

                        <div class="flex flex-col space-y-1">
                            <p class="text-sm font-medium">Preset</p>
                            <p class="text-xs text-muted-foreground">
                                {status.preset}
                            </p>
                        </div>
                    </div>
                {/if}
            {/if}
        </div>
    </Card.Content>
</Card.Root>
