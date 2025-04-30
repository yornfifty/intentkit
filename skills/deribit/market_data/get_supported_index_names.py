import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_supported_index_names_response import (
    GetSupportedIndexNamesResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetSupportedIndexNames tool
class DeribitGetSupportedIndexNamesInput(BaseModel):
    """Input for DeribitGetSupportedIndexNames tool."""

    type: Optional[Literal["all", "spot", "derivative"]] = Field(
        None, description="Optional filter for the type of cryptocurrency price index."
    )


# DeribitGetSupportedIndexNames tool to fetch supported index names from Deribit API
class DeribitGetSupportedIndexNames(DeribitBaseTool):
    """Tool to retrieve the identifiers of all supported Price Indexes from Deribit API, optionally filtered by type."""

    name: str = "get_supported_index_names"
    description: str = "Retrieves the identifiers of all supported Price Indexes."
    args_schema: Type[BaseModel] = DeribitGetSupportedIndexNamesInput

    async def _arun(
        self,
        type: Optional[Literal["all", "spot", "derivative"]] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch supported Price Index identifiers, optionally filtered by type,
        and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {}
            if type is not None:
                params["type"] = type

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(
                f"Calling /public/get_supported_index_names with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_supported_index_names", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(
                raw_json, GetSupportedIndexNamesResponse
            )
            logger.info(
                "Successfully fetched supported index names and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(f"Error getting supported index names: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get supported index names. Reason: {e}"
            ) from e
