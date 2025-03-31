<script lang="ts">
    import { getHistoryStore } from "$lib/store.svelte";
    import * as Card from "$lib/components/ui/card/index";
    import { Button } from "$lib/components/ui/button";
    import { parseReferences } from "$lib/utils";

    const historyStore = getHistoryStore();
    
    // Format date for display
    function formatDate(dateString: string): string {
        const date = new Date(dateString);
        return date.toLocaleString();
    }
    
    // Delete a history entry
    async function deleteEntry(index: number): Promise<void> {
        const confirmed = confirm("Are you sure you want to delete this history entry?");
        if (confirmed) {
            await historyStore.deleteEntry(index);
        }
    }
    
    // Clear all history
    async function clearAllHistory(): Promise<void> {
        const confirmed = confirm("Are you sure you want to delete all history? This cannot be undone.");
        if (confirmed) {
            await historyStore.clearHistory();
        }
    }
</script>

<div class="space-y-6">
    <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold">Question History</h1>
        {#if historyStore.history.length > 0}
            <Button variant="destructive" onclick={clearAllHistory} class="flex">Clear All</Button>
        {/if}
    </div>
    
    {#if historyStore.history.length === 0}
        <div class="text-center p-8 bg-muted/30 rounded-lg">
            <p class="text-muted-foreground">No history found. Ask questions to see your history here.</p>
        </div>
    {:else}
        <div class="space-y-6">
            {#each historyStore.history as entry, index}
                <Card.Root class="flex flex-col">
                    <Card.Header class="flex-shrink-0">
                        <div class="flex justify-between items-start">
                            <Card.Title class="flex-grow">Q: {entry.question}</Card.Title>
                            <div class="flex space-x-2">
                                <span class="text-xs text-muted-foreground">{formatDate(entry.timestamp)}</span>
                                <button 
                                    class="text-destructive hover:text-destructive/80 text-xs"
                                    onclick={() => deleteEntry(index)}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    </Card.Header>
                    <Card.Content class="flex-grow">
                        <div>
                            <div class="prose prose-sm mt-2 whitespace-pre-line">
                                {entry.answer}
                            </div>
                        </div>

                        {#if entry.references}
                            <details class="mt-4">
                                <summary class="cursor-pointer text-md font-semibold">References</summary>
                                <div class="mt-2 space-y-3">
                                    <ol class="mt-2 space-y-2 text-sm">
                                        {#each parseReferences(entry.references) as reference}
                                            <li class="p-2 bg-muted rounded pl-1">
                                                {reference}
                                            </li>
                                        {/each}
                                    </ol>
                                </div>
                            </details>
                        {/if}

                        {#if entry.contexts?.length}
                            <details class="mt-4">
                                <summary class="cursor-pointer text-md font-semibold">Context Details</summary>
                                <div class="mt-2 space-y-3">
                                    {#each entry.contexts as ctx}
                                        <div class="p-3 bg-muted/50 rounded text-sm">
                                            <div class="font-medium">
                                                {ctx.text_name}
                                            </div>
                                            <div class="mt-1">{ctx.context}</div>
                                            {#if ctx.score !== null}
                                                <div class="mt-1 text-xs">
                                                    Score: {ctx.score.toFixed(4)}
                                                </div>
                                            {/if}
                                        </div>
                                    {/each}
                                </div>
                            </details>
                        {/if}
                    </Card.Content>
                </Card.Root>
            {/each}
        </div>
    {/if}
</div> 