import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel  # Keep BaseModel for empty input schema

# Updated import path for base tool
from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.supporting.response.status_response import (
    StatusResponse,
)

# Updated import path for the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitStatus tool (empty as no parameters)
class DeribitStatusInput(BaseModel):
    """Input for DeribitStatus tool. Takes no parameters."""

    pass


# DeribitStatus tool to fetch platform lock status from Deribit API
class DeribitStatus(DeribitBaseTool):
    """Tool to get information about locked currencies on the Deribit platform."""

    name: str = "status"
    description: str = "Method used to get information about locked currencies."
    args_schema: Type[BaseModel] = DeribitStatusInput  # Use empty schema

    async def _arun(
        self,
        config: RunnableConfig = None,
        **kwargs,  # Accept kwargs even if not used by this specific tool
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch the platform lock status and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call (empty for this endpoint)
            params = {}

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/status with params: {params}")
            raw_json = await self.api.get("/api/v2/public/status", params=params)
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(raw_json, StatusResponse)
            logger.info("Successfully fetched platform status and format the result")
            return formatted_output

        except Exception as e:
            logger.error(f"Error getting platform status: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get platform status. Reason: {e}"
            ) from e
