<script>
    import { Button } from "$lib/components/ui/button";
    import { Textarea } from "$lib/components/ui/textarea";
    import * as Card from "$lib/components/ui/card/index";
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

    // Convert references string to an array of reference items
    function parseReferences(referencesText) {
        if (!referencesText) return [];

        // Use a regex that only matches the numbered list item patterns at the start of lines
        // This preserves the entire content of each reference
        const referenceLines = referencesText.split(/\n\s*(?=\d+\.\s+)/);

        // Process the first item which might not have a number prefix if it starts at the beginning
        const result = [];
        for (let i = 0; i < referenceLines.length; i++) {
            let line = referenceLines[i].trim();
            // If this is the first line and doesn't start with a number, skip it
            if (i === 0 && !line.match(/^\d+\.\s+/)) {
                continue;
            }
            result.push(line);
        }

        return result;
    }
</script>

<div class="space-y-6">
    <h2 class="text-lg font-semibold">Ask a Question</h2>

    <div class="space-y-4">
        <Textarea
            placeholder="Enter your question about the papers"
            bind:value={question}
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
        <Card.Root>
            <Card.Content>
                <div>
                    <div class="prose prose-sm mt-2 whitespace-pre-line">
                        {answer.answer || answer.formatted_answer}
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
