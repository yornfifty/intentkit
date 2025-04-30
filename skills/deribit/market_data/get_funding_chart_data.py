import logging
from typing import Any, Literal, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_funding_chart_data_response import (
    GetFundingChartDataResponse,
)

# Import the CSV utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetFundingChartData tool
class DeribitGetFundingChartDataInput(BaseModel):
    """Input for DeribitGetFundingChartData tool."""

    instrument_name: str = Field(
        ...,
        description="Instrument name (must be a PERPETUAL) (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first).",
    )
    length: Literal["8h", "24h", "1m"] = Field(
        ..., description="Specifies time period: 8h, 24h, or 1m (1 month)."
    )


# DeribitGetFundingChartData tool to fetch funding chart data from Deribit API
class DeribitGetFundingChartData(DeribitBaseTool):
    """Tool to retrieve funding chart data points for perpetuals from Deribit API."""

    name: str = "get_funding_chart_data"
    description: str = "Retrieve the list of the latest PERPETUAL funding chart points within a given time period (8h, 24h, 1m)."
    args_schema: Type[BaseModel] = DeribitGetFundingChartDataInput

    async def _arun(
        self,
        instrument_name: str,
        length: Literal["8h", "24h", "1m"],
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (CSV)
        """
        Fetch funding chart data points for a specific perpetual instrument and time length, return as CSV.
        """
        # Basic validation reminder
        if "PERPETUAL" not in instrument_name.upper():
            logger.warning(
                f"Instrument '{instrument_name}' might not be a perpetual. API call might fail or return unexpected results."
            )

        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "instrument_name": instrument_name,
                "length": length,
            }

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(
                f"Calling /public/get_funding_chart_data with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_funding_chart_data", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(raw_json, GetFundingChartDataResponse)
            logger.info(
                f"Successfully fetched funding chart data for {instrument_name} ({length}) and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(
                f"Error getting funding chart data for {instrument_name}: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get funding chart data for {instrument_name}. Reason: {e}"
            ) from e
