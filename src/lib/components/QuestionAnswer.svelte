<script>
    import { Button } from "$lib/components/ui/button";
    import paperQAClient from "$lib/paperqa-client";

    let question = $state("");
    let answer = $state(null);
    let isLoading = $state(false);
    let error = $state("");

    async function askQuestion(event) {
        event.preventDefault();
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
            } else {
                error = result.message || "Failed to get answer";
            }
        } catch (err) {
            console.error("Error asking question:", err);
            error = `Error asking question: ${err.message}`;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="space-y-6">
    <h2 class="text-lg font-semibold">Ask a Question</h2>

    <div class="space-y-4">
        <textarea
            class="w-full p-3 border rounded h-32"
            placeholder="Enter your question about the papers"
            bind:value={question}
        ></textarea>

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
        <div class="border rounded p-4 space-y-4">
            <div>
                <h3 class="text-md font-semibold">Answer:</h3>
                <div class="prose prose-sm mt-2">
                    {answer.formatted_answer || answer.answer}
                </div>
            </div>

            {#if answer.references?.length}
                <div>
                    <h3 class="text-md font-semibold">References:</h3>
                    <ul class="mt-2 space-y-2 text-sm">
                        {#each answer.references as ref}
                            <li class="p-2 bg-muted rounded">
                                {ref}
                            </li>
                        {/each}
                    </ul>
                </div>
            {/if}

            {#if answer.contexts?.length}
                <details class="mt-4">
                    <summary class="cursor-pointer text-md font-semibold"
                        >Context Details</summary
                    >
                    <div class="mt-2 space-y-3">
                        {#each answer.contexts as ctx}
                            <div class="p-3 bg-muted/50 rounded text-sm">
                                <div class="font-medium">{ctx.text_name}</div>
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
        </div>
    {/if}
</div>
