<script>
    import { resolveResource } from "@tauri-apps/api/path";
    import { Command } from "@tauri-apps/plugin-shell";

    let outputMessage = $state("");

    $effect(() => {
        launchPythonSidecar();
    });

    async function launchPythonSidecar() {
        const pythonFilePath = await resolveResource("hello.py");
        const command = Command.sidecar("binaries/uv", ["run", pythonFilePath]);
        const output = await command.execute();

        console.log(output);
        outputMessage = output.stdout;
    }
</script>

<main>
    <h1>Welcome to Nova!</h1>
    <p>{outputMessage}</p>
</main>
