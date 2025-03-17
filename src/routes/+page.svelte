<script>
    import { resolveResource } from "@tauri-apps/api/path";
    import { Command } from "@tauri-apps/plugin-shell";
    import { onDestroy } from "svelte";

    let errorMessage = $state("");
    let pythonCommand = null;

    $effect(() => {
        launchPythonSidecar();
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
        } catch (error) {
            console.error("Error launching Python sidecar:", error);
            errorMessage = `Error: ${error.message}`;
        }
    }

    // Clean up the process when the component is destroyed
    onDestroy(() => {
        if (pythonCommand) {
            console.log("Killing Python server process");
            pythonCommand.kill();
        }
    });
</script>

<main>
    <h1>Welcome to Nova!</h1>
    {#if errorMessage}
        <p>{errorMessage}</p>
    {/if}
</main>
