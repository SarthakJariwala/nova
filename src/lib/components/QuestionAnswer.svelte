<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import { Textarea } from "$lib/components/ui/textarea";
    import * as Card from "$lib/components/ui/card/index";
    import paperQAClient from "$lib/paperqa-client";
    import { getHistoryStore, getAnswerStore } from "$lib/store.svelte";
    import { parseReferences } from "$lib/utils";

    const qaStore = getAnswerStore();
    const qa = qaStore.qa;
    
    const historyStore = getHistoryStore();

    async function askQuestion() {
        if (!qa.question.trim()) {
            qa.error = "Please enter a question";
            return;
        }

        qa.error = "";
        qa.isLoading = true;

        try {
            qa.answer = ""
            const result = await paperQAClient.ask(qa.question);
            if (result.status === "success") {
                qa.answer = result;
                
                // Save to history
                await historyStore.addEntry({
                    question: qa.question,
                    answer: qa.answer?.answer || qa.answer?.formatted_answer || "",
                    references: qa.answer?.references,
                    contexts: qa.answer?.contexts
                });
            } else {
                qa.error = result.message || "Failed to get answer";
            }
        } catch (err: unknown) {
            console.error("Error asking question:", err);
            const errMessage = err instanceof Error ? err.message : String(err);
            qa.error = `Error asking question: ${errMessage}`;
        } finally {
            qa.isLoading = false;
        }
    }
</script>

<div class="space-y-6">
    <div class="space-y-4">
        <Textarea
            placeholder="Enter your question about the papers"
            bind:value={qa.question}
            class="w-full"
        ></Textarea>

        <Button
            onclick={askQuestion}
            disabled={qa.isLoading}
            variant="default"
            class="w-full"
        >
            {qa.isLoading ? "Analyzing..." : "Ask Question"}
        </Button>
    </div>

    {#if qa.error}
        <div
            class="p-3 bg-destructive/20 text-destructive border border-destructive rounded"
        >
            {qa.error}
        </div>
    {/if}

    {#if qa.answer}
        <Card.Root class="flex flex-col">
            <Card.Content class="flex-grow">
                <div>
                    <div class="prose prose-sm mt-2 whitespace-pre-line">
                        {qa.answer?.answer || qa.answer?.formatted_answer || ""}
                    </div>
                </div>

                {#if qa.answer.references}
                    <details class="mt-4">
                        <summary class="cursor-pointer text-md font-semibold"
                            >References</summary
                        >
                        <div class="mt-2 space-y-3">
                            <ol class="mt-2 space-y-2 text-sm">
                                {#each parseReferences(qa.answer.references) as reference}
                                    <li class="p-2 bg-muted rounded pl-1">
                                        {reference}
                                    </li>
                                {/each}
                            </ol>
                        </div>
                    </details>
                {/if}

                {#if qa.answer.contexts?.length}
                    <details class="mt-4">
                        <summary class="cursor-pointer text-md font-semibold"
                            >Context Details</summary
                        >
                        <div class="mt-2 space-y-3">
                            {#each qa.answer.contexts as ctx}
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
    {/if}
</div>
