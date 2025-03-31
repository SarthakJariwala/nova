<script>
    import Layout from "$lib/components/Layout.svelte";
    import PaperDirectorySelector from "$lib/components/PaperDirectorySelector.svelte";
    import PaperQASettings from "$lib/components/PaperQASettings.svelte";
    import QuestionAnswer from "$lib/components/QuestionAnswer.svelte";
    import AppStatus from "$lib/components/AppStatus.svelte";
    import History from "$lib/components/History.svelte";
    import { resolveResource } from "@tauri-apps/api/path";
    import { Command } from "@tauri-apps/plugin-shell";
    import paperQAClient from "$lib/paperqa-client";
    import { setUserSettings, setHistoryStore, setAnswerStore } from "$lib/store.svelte";

    let activeTab = $state("papers");

    // Initialize stores
    setUserSettings();
    setHistoryStore();
    setAnswerStore();

    let pythonCommand = null;
    let pythonChildProcess = null;
    let errorMessage = $state("");

    $effect(() => {
        launchPythonSidecar();

        return () => {
            if (pythonChildProcess) {
                console.log("Killing Python server process");
                pythonChildProcess.kill();
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
            pythonChildProcess = await pythonCommand.execute();
            console.log("Python server started");

            // Wait a moment for the server to start up
            await new Promise((resolve) => setTimeout(resolve, 1000));

            // Connect to the server
            await paperQAClient.connect();
        } catch (error) {
            console.error("Error launching Python sidecar:", error);
            const errMessage = error instanceof Error ? error.message : String(error);
            errorMessage = `Error: ${errMessage}`;
        }
    }
</script>

<Layout>
    {#if errorMessage}
        <div
            class="p-4 bg-destructive/20 text-destructive border border-destructive rounded m-4"
        >
            {errorMessage}
        </div>
    {/if}
    <svelte:fragment slot="sidebar">
        <div class="space-y-1">
            <button
                class="w-full text-left px-3 py-2 rounded text-sm {activeTab ===
                'papers'
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50'}"
                onclick={() => (activeTab = "papers")}
            >
                Papers
            </button>

            <button
                class="w-full text-left px-3 py-2 rounded text-sm {activeTab ===
                'ask'
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50'}"
                onclick={() => (activeTab = "ask")}
            >
                Ask Questions
            </button>
            
            <button
                class="w-full text-left px-3 py-2 rounded text-sm {activeTab ===
                'history'
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50'}"
                onclick={() => (activeTab = "history")}
            >
                History
            </button>

            <button
                class="w-full text-left px-3 py-2 rounded text-sm {activeTab ===
                'settings'
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50'}"
                onclick={() => (activeTab = "settings")}
            >
                Settings
            </button>
        </div>

        <div class="mt-6">
            <AppStatus />
        </div>
    </svelte:fragment>

    <div>
        {#if activeTab === "papers"}
            <div class="space-y-6">
                <h1 class="text-2xl font-bold">Paper Management</h1>
                <p class="text-muted-foreground">
                    Select a folder containing papers to analyze
                </p>

                <PaperDirectorySelector />
            </div>
        {:else if activeTab === "ask"}
            <div class="space-y-6">
                <h1 class="text-2xl font-bold">Ask Questions</h1>
                <p class="text-muted-foreground">
                    Ask questions about your papers
                </p>

                <QuestionAnswer />
            </div>
        {:else if activeTab === "history"}
            <div class="space-y-6">
                <History />
            </div>
        {:else if activeTab === "settings"}
            <div class="space-y-6">
                <h1 class="text-2xl font-bold">Settings</h1>
                <p class="text-muted-foreground">Configure PaperQA settings</p>

                <PaperQASettings />
            </div>
        {/if}
    </div>
</Layout>
