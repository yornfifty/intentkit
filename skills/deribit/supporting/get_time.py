import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel  # Keep BaseModel for empty input schema

# Updated import path for base tool
from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.supporting.response.get_time_response import (
    GetTimeResponse,
)

# Updated import path for the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetTime tool (empty as no parameters)
class DeribitGetTimeInput(BaseModel):
    """Input for DeribitGetTime tool. Takes no parameters."""

    pass


# DeribitGetTime tool to fetch current server time from Deribit API
class DeribitGetTime(DeribitBaseTool):
    """Tool to retrieve the current Deribit server time (in milliseconds)."""

    name: str = "get_time"
    description: str = (
        "Retrieves the current time (in milliseconds). Useful for checking clock skew."
    )
    args_schema: Type[BaseModel] = DeribitGetTimeInput  # Use empty schema

    async def _arun(
        self,
        config: RunnableConfig = None,
        **kwargs,  # Accept kwargs even if not used by this specific tool
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch the current Deribit server time and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit (might be less critical for this endpoint, but keep for consistency)
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call (empty for this endpoint)
            params = {}

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/get_time with params: {params}")
            raw_json = await self.api.get("/api/v2/public/get_time", params=params)
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(raw_json, GetTimeResponse)
            logger.info("Successfully fetched server time and format the result")
            return formatted_output

        except Exception as e:
            logger.error(f"Error getting server time: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get server time. Reason: {e}"
            ) from e
