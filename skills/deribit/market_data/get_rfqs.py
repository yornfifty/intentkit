import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_rfqs_response import (
    GetRFQsResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetRFQs tool
class DeribitGetRFQsInput(BaseModel):
    """Input for DeribitGetRFQs tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"] = Field(
        ..., description="The currency symbol."
    )
    kind: Optional[
        Literal["future", "option", "spot", "future_combo", "option_combo"]
    ] = Field(None, description="Instrument kind filter (optional).")


# DeribitGetRFQs tool to fetch active RFQs from Deribit API
class DeribitGetRFQs(DeribitBaseTool):
    """Tool to retrieve active Requests For Quotes (RFQs) for instruments in a given currency from Deribit API."""

    name: str = "get_rfqs"
    description: str = "Retrieve active RFQs for instruments in given currency."
    args_schema: Type[BaseModel] = DeribitGetRFQsInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"],
        kind: Optional[
            Literal["future", "option", "spot", "future_combo", "option_combo"]
        ] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch active RFQs for a specific currency, optionally filtered by kind,
        and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {"currency": currency}
            if kind is not None:
                params["kind"] = kind

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/get_rfqs with params: {params}")
            raw_json = await self.api.get("/api/v2/public/get_rfqs", params=params)
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(raw_json, GetRFQsResponse)
            logger.info(
                f"Successfully fetched RFQs for {currency} and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(f"Error getting RFQs for {currency}: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get RFQs for {currency}. Reason: {e}"
            ) from e
