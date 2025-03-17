## How to Use the Server

### Start the server:

```bash
uv run paperqa_server.py
```

This will start the ZeroRPC server on the default address (tcp://127.0.0.1:4242).

### API Methods

The server exposes the following methods that can be called via any ZeroRPC client:

1. **initialize(paper_dir, ...)** - Initialize the PaperQA instance with your papers directory and other settings
2. **ask(question)** - Ask a question using the configured PaperQA instance
3. **update_settings(...)** - Update the settings of the PaperQA instance
4. **get_preset_names()** - Get a list of available preset configurations
5. **get_status()** - Get the current status of the PaperQA service

### Example Workflow

The typical workflow with this server would be:

1. Connect to the server
2. Call `initialize()` with your papers directory and settings
3. Call `ask()` with your questions
4. Optionally call `update_settings()` to change settings
5. Continue asking questions as needed
