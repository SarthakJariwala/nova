"""
PaperQA API - A class-based wrapper for the PaperQA library.

This module provides a simple class to interact with PaperQA in your projects.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from paperqa import Settings, ask
from paperqa.settings import AgentSettings, AnswerSettings, IndexSettings


class PaperQA:
    """
    A wrapper for the PaperQA library.
    """

    def __init__(
        self,
        paper_dir: Path,
        llm: str = "gpt-4o-2024-11-20",
        summary_llm: str = "gpt-4o-2024-11-20",
        agent_llm: str = "gpt-4o-2024-11-20",
        embedding: str = "text-embedding-3-small",
        temperature: float = 0.0,
        verbosity: int = 0,
        evidence_k: int = 10,
        max_sources: int = 5,
        chunk_size: int = 5000,
        use_tier1_limits: bool = False,
        rate_limit: Optional[str] = None,
        preset: Optional[str] = None,
        index_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the PaperQA wrapper.

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
            api_key: API key for the LLM provider
        """
        # Check if paper directory exists
        paper_dir = Path(paper_dir).expanduser()
        if not paper_dir.is_dir():
            raise ValueError(f"Paper directory '{paper_dir}' does not exist")

        self.paper_dir = str(paper_dir)
        self.llm = llm
        self.summary_llm = summary_llm
        self.agent_llm = agent_llm
        self.embedding = embedding
        self.temperature = temperature
        self.verbosity = verbosity
        self.evidence_k = evidence_k
        self.max_sources = max_sources
        self.chunk_size = chunk_size
        self.use_tier1_limits = use_tier1_limits
        self.rate_limit = rate_limit
        self.preset = preset
        self.index_name = index_name
        self.api_key = api_key

        if self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key

        # Create settings
        self._create_settings()

    def _create_settings(self):
        """Create the settings object."""
        # Build settings dictionary
        settings_dict = {
            "paper_directory": self.paper_dir,
            "temperature": self.temperature,
            "verbosity": self.verbosity,
            "llm": self.llm,
            "summary_llm": self.summary_llm,
            "embedding": self.embedding,
            "answer": AnswerSettings(
                evidence_k=self.evidence_k, answer_max_sources=self.max_sources
            ),
            "agent": AgentSettings(
                agent_llm=self.agent_llm,
                index=IndexSettings(
                    paper_directory=self.paper_dir, name=self.index_name
                ),
            ),
            "parsing": {"chunk_size": self.chunk_size},
        }

        # Use preset if specified
        if self.preset:
            preset_settings = Settings.from_name(self.preset)
            preset_dict = preset_settings.model_dump()
            # Override preset with our specific settings
            for key, value in settings_dict.items():
                preset_dict[key] = value
            self.settings = Settings(**preset_dict)
        else:
            self.settings = Settings(**settings_dict)

        # Configure rate limits
        if self.use_tier1_limits:
            tier1_settings = Settings.from_name("tier1_limits")
            self.settings = Settings(
                **{
                    **self.settings.model_dump(),
                    "llm_config": tier1_settings.llm_config,
                    "summary_llm_config": tier1_settings.summary_llm_config,
                    "agent": AgentSettings(
                        **{
                            **self.settings.agent.model_dump(),
                            "agent_llm_config": tier1_settings.agent.agent_llm_config,
                        }
                    ),
                }
            )
        elif self.rate_limit:
            rate_limit_config = {"rate_limit": {self.llm: self.rate_limit}}
            self.settings = Settings(
                **{
                    **self.settings.model_dump(),
                    "llm_config": rate_limit_config,
                    "summary_llm_config": rate_limit_config,
                    "agent": AgentSettings(
                        **{
                            **self.settings.agent.model_dump(),
                            "agent_llm_config": rate_limit_config,
                        }
                    ),
                }
            )

    def ask(self, question: str) -> Dict:
        """
        Ask a question to PaperQA.

        Args:
            question: The question to ask

        Returns:
            Dict containing the response with answer, formatted_answer, references, etc.
        """
        # Check if API key is set
        if not self.is_api_key_configured():
            return {
                "status": "error",
                "message": "API key not configured. Please set it in Settings.",
            }
        # Run PaperQA
        response = ask(question, settings=self.settings)

        # Return result as a dictionary
        return {
            "question": question,
            "answer": response.session.answer,
            "formatted_answer": response.session.formatted_answer,
            "references": response.session.references,
            "contexts": [
                {
                    "context": ctx.context,
                    "text_name": ctx.text.name
                    if hasattr(ctx, "text") and hasattr(ctx.text, "name")
                    else "",
                    "score": float(ctx.score) if hasattr(ctx, "score") else None,
                }
                for ctx in response.session.contexts
            ]
            if hasattr(response.session, "contexts")
            else [],
        }

    def update_settings(self, **kwargs):
        """
        Update settings with new values.

        Args:
            **kwargs: Key-value pairs of settings to update
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Update API key in environment if it was changed
        if "api_key" in kwargs and kwargs["api_key"]:
            os.environ["OPENAI_API_KEY"] = kwargs["api_key"]

        # Recreate settings with new values
        self._create_settings()

    def is_api_key_configured(self) -> bool:
        """
        Check if the API key is configured.

        Returns:
            True if API key is configured, False otherwise.
        """
        return bool(self.api_key or os.environ.get("OPENAI_API_KEY"))

    @staticmethod
    def get_preset_names() -> List[str]:
        """
        Get a list of available preset configuration names.

        Returns:
            List of preset names
        """
        return [
            "high_quality",
            "fast",
            "wikicrow",
            "contracrow",
            "debug",
            "tier1_limits",
        ]
