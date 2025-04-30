import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel  # Keep BaseModel for empty input schema

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_index_price_names_response import (
    GetIndexPriceNamesResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetIndexPriceNames tool (empty as no parameters)
class DeribitGetIndexPriceNamesInput(BaseModel):
    """Input for DeribitGetIndexPriceNames tool. Takes no parameters."""

    pass


# DeribitGetIndexPriceNames tool to fetch supported index price names from Deribit API
class DeribitGetIndexPriceNames(DeribitBaseTool):
    """Tool to retrieve the identifiers of all supported Price Indexes from Deribit API."""

    name: str = "get_index_price_names"
    description: str = "Retrieves the identifiers of all supported Price Indexes."
    args_schema: Type[BaseModel] = DeribitGetIndexPriceNamesInput  # Use empty schema

    async def _arun(
        self,
        config: RunnableConfig = None,
        **kwargs,  # Accept kwargs even if not used by this specific tool
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch all supported Price Index identifiers and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call (empty for this endpoint)
            params = {}

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/get_index_price_names with params: {params}")
            raw_json = await self.api.get(
                "/api/v2/public/get_index_price_names", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(raw_json, GetIndexPriceNamesResponse)
            logger.info("Successfully fetched index price names and format the result")
            return formatted_output

        except Exception as e:
            logger.error(f"Error getting index price names: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get index price names. Reason: {e}"
            ) from e
