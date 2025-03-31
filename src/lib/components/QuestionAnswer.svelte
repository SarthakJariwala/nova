<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import { Textarea } from "$lib/components/ui/textarea";
    import * as Card from "$lib/components/ui/card/index";
    import paperQAClient from "$lib/paperqa-client";
    import { getHistoryStore } from "$lib/store.svelte";
    import { parseReferences } from "$lib/utils";

    interface AnswerContext {
        text_name: string;
        context: string;
        score: number | null;
    }
    
    interface AnswerResponse {
        status: string;
        message?: string;
        answer?: string;
        formatted_answer?: string;
        references?: string;
        contexts?: AnswerContext[];
    }

    let question = $state("");
    let answer = $state<AnswerResponse | null>(null);
    let isLoading = $state(false);
    let error = $state("");
    
    // Get the history store
    const historyStore = getHistoryStore();

    async function askQuestion() {
        if (!question.trim()) {
            error = "Please enter a question";
            return;
        }

        error = "";
        isLoading = true;

        try {
            const result = await paperQAClient.ask(question);
            if (result.status === "success") {
                answer = result;
                
                // Save to history
                await historyStore.addEntry({
                    question,
                    answer: answer?.answer || answer?.formatted_answer || "",
                    references: answer?.references,
                    contexts: answer?.contexts
                });
            } else {
                error = result.message || "Failed to get answer";
            }
        } catch (err: unknown) {
            console.error("Error asking question:", err);
            const errMessage = err instanceof Error ? err.message : String(err);
            error = `Error asking question: ${errMessage}`;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="space-y-6">
    <div class="space-y-4">
        <Textarea
            placeholder="Enter your question about the papers"
            bind:value={question}
            class="w-full"
        ></Textarea>

        <Button
            onclick={askQuestion}
            disabled={isLoading}
            variant="default"
            class="w-full"
        >
            {isLoading ? "Processing..." : "Ask Question"}
        </Button>
    </div>

    {#if error}
        <div
            class="p-3 bg-destructive/20 text-destructive border border-destructive rounded"
        >
            {error}
        </div>
    {/if}

    {#if answer}
        <Card.Root class="flex flex-col">
            <Card.Content class="flex-grow">
                <div>
                    <div class="prose prose-sm mt-2 whitespace-pre-line">
                        {answer.answer || answer.formatted_answer || ""}
                    </div>
                </div>

                {#if answer.references}
                    <details class="mt-4">
                        <summary class="cursor-pointer text-md font-semibold"
                            >References</summary
                        >
                        <div class="mt-2 space-y-3">
                            <ol class="mt-2 space-y-2 text-sm">
                                {#each parseReferences(answer.references) as reference}
                                    <li class="p-2 bg-muted rounded pl-1">
                                        {reference}
                                    </li>
                                {/each}
                            </ol>
                        </div>
                    </details>
                {/if}

                {#if answer.contexts?.length}
                    <details class="mt-4">
                        <summary class="cursor-pointer text-md font-semibold"
                            >Context Details</summary
                        >
                        <div class="mt-2 space-y-3">
                            {#each answer.contexts as ctx}
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
