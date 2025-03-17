<script>
    import Layout from "$lib/components/Layout.svelte";
    import PaperDirectorySelector from "$lib/components/PaperDirectorySelector.svelte";
    import PaperQASettings from "$lib/components/PaperQASettings.svelte";
    import QuestionAnswer from "$lib/components/QuestionAnswer.svelte";
    import AppStatus from "$lib/components/AppStatus.svelte";

    let activeTab = $state("papers");
</script>

<Layout>
    <svelte:fragment slot="sidebar">
        <div class="space-y-1">
            <button
                class="w-full text-left px-3 py-2 rounded text-sm {activeTab ===
                'papers'
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50'}"
                on:click={() => (activeTab = "papers")}
            >
                Papers
            </button>

            <button
                class="w-full text-left px-3 py-2 rounded text-sm {activeTab ===
                'ask'
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50'}"
                on:click={() => (activeTab = "ask")}
            >
                Ask Questions
            </button>

            <button
                class="w-full text-left px-3 py-2 rounded text-sm {activeTab ===
                'settings'
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50'}"
                on:click={() => (activeTab = "settings")}
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
                    Select a directory containing papers to analyze
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
        {:else if activeTab === "settings"}
            <div class="space-y-6">
                <h1 class="text-2xl font-bold">Settings</h1>
                <p class="text-muted-foreground">Configure PaperQA settings</p>

                <PaperQASettings />
            </div>
        {/if}
    </div>
</Layout>
