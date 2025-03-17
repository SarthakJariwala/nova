# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "paper-qa",
#     "pyzmq",
# ]
# ///
import atexit
import logging
import os
import signal
import sys
import threading
from typing import Any, Dict, Optional

import zmq
from paperqa_api import PaperQA

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PaperQAService:
    """
    ZMQ-based service that exposes the PaperQA API (Single Instance).
    """

    def __init__(self):
        """Initialize the service without a PaperQA instance yet."""
        self.paperqa = None
        self.is_initialized = False
        logger.info("PaperQA service initialized (waiting for configuration)")

    def initialize(
        self,
        paper_dir: str,
        llm: str = "gpt-4o-2024-11-20",
        summary_llm: str = "gpt-4o-2024-11-20",
        agent_llm: str = "gpt-4o-2024-11-20",
        embedding: str = "text-embedding-3-small",
        temperature: float = 0.0,
        verbosity: int = 0,
        evidence_k: int = 10,
        max_sources: int = 5,
        chunk_size: int = 5000,
        use_tier1_limits: bool = True,
        rate_limit: Optional[str] = None,
        preset: Optional[str] = None,
        index_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initialize the PaperQA instance with the given settings.

        Args:
            paper_dir: Directory containing papers to analyze
            llm: Main LLM to use
            summary_llm: LLM for summaries
            agent_llm: LLM for agent
            embedding: Embedding model to use
            temperature: Temperature for LLM
            verbosity: Verbosity level (0-3)
            evidence_k: Number of evidence pieces to retrieve
            max_sources: Max number of sources for an answer
            chunk_size: Characters per chunk
            use_tier1_limits: Use tier1 rate limits
            rate_limit: Custom rate limit string (e.g. '30000 per 1 minute')
            preset: Use a preset configuration
            index_name: Custom name for the index

        Returns:
            Dict with status message
        """
        try:
            # Create a new PaperQA instance
            self.paperqa = PaperQA(
                paper_dir=paper_dir,
                llm=llm,
                summary_llm=summary_llm,
                agent_llm=agent_llm,
                embedding=embedding,
                temperature=temperature,
                verbosity=verbosity,
                evidence_k=evidence_k,
                max_sources=max_sources,
                chunk_size=chunk_size,
                use_tier1_limits=use_tier1_limits,
                rate_limit=rate_limit,
                preset=preset,
                index_name=index_name,
            )
            self.is_initialized = True
            logger.info(
                f"PaperQA instance initialized with paper directory: {paper_dir}"
            )
            return {
                "status": "success",
                "message": "PaperQA initialized successfully",
            }
        except Exception as e:
            logger.error(f"Error initializing PaperQA: {str(e)}")
            return {"status": "error", "message": str(e)}

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question using the PaperQA instance.

        Args:
            question: The question to ask

        Returns:
            Dict with the answer and other information
        """
        if not self.is_initialized:
            logger.error("PaperQA not initialized")
            return {
                "status": "error",
                "message": "PaperQA not initialized. Call initialize() first.",
            }

        try:
            logger.info(f"Asking question: {question}")
            result = self.paperqa.ask(question)
            return {"status": "success", **result}
        except Exception as e:
            logger.error(f"Error asking question: {str(e)}")
            return {"status": "error", "message": str(e)}

    def update_settings(self, **kwargs) -> Dict[str, Any]:
        """
        Update settings for the PaperQA instance.

        Args:
            **kwargs: Key-value pairs of settings to update

        Returns:
            Dict with status message
        """
        if not self.is_initialized:
            logger.error("PaperQA not initialized")
            return {
                "status": "error",
                "message": "PaperQA not initialized. Call initialize() first.",
            }

        try:
            logger.info(f"Updating settings: {kwargs}")
            self.paperqa.update_settings(**kwargs)
            return {
                "status": "success",
                "message": "Settings updated successfully",
            }
        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_preset_names(self) -> Dict[str, Any]:
        """
        Get a list of available preset configuration names.

        Returns:
            Dict with list of preset names
        """
        try:
            presets = PaperQA.get_preset_names()
            return {"status": "success", "presets": presets}
        except Exception as e:
            logger.error(f"Error getting preset names: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the PaperQA service.

        Returns:
            Dict with status information
        """
        if not self.is_initialized:
            return {
                "status": "not_initialized",
                "message": "PaperQA not initialized. Call initialize() first.",
            }

        return {
            "status": "initialized",
            "paper_dir": self.paperqa.paper_dir.name,
            "llm": self.paperqa.llm,
            "embedding": self.paperqa.embedding,
            "preset": self.paperqa.preset or "none",
        }


class PaperQAServer:
    """
    ZMQ-based server for PaperQA.
    """

    def __init__(self, host="*", port=5555):
        """
        Initialize the server.

        Args:
            host: Host to bind to (default: "*" - all interfaces)
            port: Port to bind to (default: 5555)
        """
        self.host = host
        self.port = port
        self.running = False
        self.thread = None
        self.service = PaperQAService()
        self.socket = None
        self.context = None

        # Set up signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Register cleanup function to run on exit
        atexit.register(self.cleanup)

        # Log the process ID for debugging
        logger.info(f"Server starting with PID: {os.getpid()}")

    def cleanup(self):
        """Clean up resources when the process exits."""
        logger.info("Cleaning up server resources...")
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")

        if self.context:
            try:
                self.context.term()
            except Exception as e:
                logger.error(f"Error terminating ZMQ context: {e}")

        logger.info("Server cleanup complete")

    def signal_handler(self, sig, frame):
        """Handle signals to gracefully shut down the server."""
        signal_name = "SIGTERM" if sig == signal.SIGTERM else "SIGINT"
        logger.info(f"Received {signal_name} signal, stopping server...")
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)
        sys.exit(0)

    def handle_request(self, socket):
        """
        Handle a single request from a client.

        Args:
            socket: ZMQ socket to receive from and send to
        """
        try:
            # Receive request
            request_data = socket.recv_json()

            # Extract method and params
            method = request_data.get("method")
            params = request_data.get("params", {})

            logger.debug(f"Received request: {method} with params: {params}")

            # Call the appropriate method
            if method == "initialize":
                result = self.service.initialize(**params)
            elif method == "ask":
                question = params.get("question", "")
                result = self.service.ask(question)
            elif method == "update_settings":
                result = self.service.update_settings(**params)
            elif method == "get_preset_names":
                result = self.service.get_preset_names()
            elif method == "get_status":
                result = self.service.get_status()
            else:
                result = {
                    "status": "error",
                    "message": f"Unknown method: {method}",
                }

            # Send response
            socket.send_json(result)

        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            # Send error response
            socket.send_json(
                {"status": "error", "message": f"Server error: {str(e)}"}
            )

    def run(self):
        """Run the server in a loop."""
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

        endpoint = f"tcp://{self.host}:{self.port}"
        self.socket.bind(endpoint)

        logger.info(f"PaperQA ZMQ server started on {endpoint}")

        self.running = True
        while self.running:
            try:
                # Wait for next request from client with a timeout
                if self.socket.poll(timeout=500) != 0:  # timeout in ms
                    self.handle_request(self.socket)
            except zmq.ZMQError as e:
                logger.error(f"ZMQ error: {str(e)}")
                # Continue running unless we're shutting down
                if not self.running:
                    break
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")

        # Cleanup happens in the cleanup method
        logger.info("Server stopped.")

    def start(self):
        """Start the server in a background thread."""
        if self.thread and self.thread.is_alive():
            logger.warning("Server is already running.")
            return

        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Server started in background thread.")

    def stop(self):
        """Stop the server."""
        logger.info("Stopping server...")
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)
        logger.info("Server stopped.")


if __name__ == "__main__":
    # Start the server directly if this file is run as a script
    server = PaperQAServer()
    server.run()  # This will block until the server is stopped
