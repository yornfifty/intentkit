"""Base class for all Deribit tools."""

import logging
from typing import Type

from pydantic import BaseModel, Field

from abstracts.skill import SkillStoreABC
from skills.base import IntentKitSkill, SkillContext
from skills.deribit.api import DeribitApi

logger = logging.getLogger(__name__)


class DeribitBaseTool(IntentKitSkill):
    """Base class for Deribit tools.

    This class provides common functionality for all Deribit API tools:
    - Rate limiting
    - API client handling
    - State management through skill_store
    """

    name: str = Field(description="The name of the tool")
    description: str = Field(description="A description of what the tool does")
    args_schema: Type[BaseModel]
    skill_store: SkillStoreABC = Field(
        ..., description="The skill store for persisting data"
    )
    api: DeribitApi = Field(
        ..., description="API service to interact with Deribit's backend"
    )

    @property
    def category(self) -> str:
        return "deribit"

    async def apply_rate_limit(self, context: SkillContext) -> None:
        """
        Applies rate limiting ONLY if specified in the agent's config ('skill_config').
        Checks for 'rate_limit_number' and 'rate_limit_minutes'.
        If not configured, NO rate limiting is applied.
        Raises ConnectionAbortedError if the configured limit is exceeded.
        """
        skill_config = context.config
        user_id = context.user_id

        # Get agent-specific limits safely
        limit_num = skill_config.get("rate_limit_number")
        limit_min = skill_config.get("rate_limit_minutes")

        # Apply limit ONLY if both values are present and valid (truthy check handles None and 0)
        if limit_num and limit_min:
            limit_source = "Agent"
            logger.debug(
                f"Applying {limit_source} rate limit ({limit_num}/{limit_min} min) for user {user_id} on {self.name}"
            )
            await self.user_rate_limit_by_category(user_id, limit_num, limit_min)
        else:
            # No valid agent configuration found, so do nothing.
            logger.debug(
                f"No agent rate limits configured for category '{self.category}'. Skipping rate limit for user {user_id}."
            )
