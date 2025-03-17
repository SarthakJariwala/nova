<script>
    import { resolveResource } from "@tauri-apps/api/path";
    import { Command } from "@tauri-apps/plugin-shell";
    import paperQAClient from "$lib/paperqa-client";

    let pythonCommand = null;
    let errorMessage = $state("");

    $effect(() => {
        launchPythonSidecar();

        return () => {
            if (pythonCommand) {
                console.log("Killing Python server process");
                pythonCommand.kill();
            }

            paperQAClient.close().catch((err) => {
                console.error("Error closing ZMQ connection:", err);
            });
        };
    });

    async function launchPythonSidecar() {
        try {
            const pythonFilePath = await resolveResource(
                "python_backend/paperqa_server.py",
            );
            console.log("Python file path:", pythonFilePath);

            // Create the command
            pythonCommand = Command.sidecar("binaries/uv", [
                "run",
                pythonFilePath,
            ]);

            // Start the process
            await pythonCommand.execute();
            console.log("Python server started");

            // Wait a moment for the server to start up
            await new Promise((resolve) => setTimeout(resolve, 1000));

            // Connect to the server
            await paperQAClient.connect();
        } catch (error) {
            console.error("Error launching Python sidecar:", error);
            errorMessage = `Error: ${error.message}`;
        }
    }
</script>

<div class="flex h-screen bg-background">
    <aside class="w-64 bg-sidebar border-r border-sidebar-border">
        <div class="p-4">
            <h1 class="text-xl font-bold text-sidebar-foreground">Nova</h1>
            <p class="text-sm text-sidebar-foreground/70">PaperQA Interface</p>
        </div>

        <nav class="p-2">
            <slot name="sidebar" />
        </nav>
    </aside>

    <main class="flex-1 overflow-auto">
        {#if errorMessage}
            <div
                class="p-4 bg-destructive/20 text-destructive border border-destructive rounded m-4"
            >
                {errorMessage}
            </div>
        {/if}

        <div class="p-6">
            <slot />
        </div>
    </main>
</div>
