import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_currencies_response import (
    GetCurrenciesResponse,
)

# Import the CSV utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetCurrencies tool (empty as no parameters)
class DeribitGetCurrenciesInput(BaseModel):
    """Input for DeribitGetCurrencies tool. Takes no parameters."""

    pass


# DeribitGetCurrencies tool to fetch supported currencies from Deribit API
class DeribitGetCurrencies(DeribitBaseTool):
    """Tool to retrieve all cryptocurrencies supported by the Deribit API."""

    name: str = "get_currencies"
    description: str = "Retrieves all cryptocurrencies supported by the API."
    args_schema: Type[BaseModel] = DeribitGetCurrenciesInput  # Use empty schema

    async def _arun(
        self,
        config: RunnableConfig = None,
        **kwargs,  # Accept kwargs even if not used by this specific tool
    ) -> Any:  # Return type is str (CSV)
        """
        Fetch all supported currencies and return them as a CSV string.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call (empty for this endpoint)
            params = {}

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/get_currencies with params: {params}")
            raw_json = await self.api.get(
                "/api/v2/public/get_currencies", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to CSV string using the utility
            # Pass the response model to guide CSV conversion, especially for nested lists
            formatted_result = format_json_result(raw_json, GetCurrenciesResponse)
            logger.info(
                "Successfully fetched supported currencies and format the result"
            )
            return formatted_result

        except Exception as e:
            logger.error(f"Error getting currencies: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get currencies. Reason: {e}"
            ) from e
