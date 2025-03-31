<div class="flex h-screen bg-background">
    <aside class="w-64 bg-sidebar border-r border-sidebar-border">
        <div class="p-4">
            <h1 class="text-xl font-bold text-sidebar-foreground">Nova</h1>
            <p class="text-sm text-sidebar-foreground/70">
                A PaperQA Interface
            </p>
        </div>

        <nav class="p-2">
            <slot name="sidebar" />
        </nav>
    </aside>

    <main class="flex-1 overflow-auto">
        <div class="p-6">
            <slot />
        </div>
    </main>
</div>
