import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_contract_size_response import (
    GetContractSizeResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

# Import the CSV utility

logger = logging.getLogger(__name__)


# Input schema for DeribitGetContractSize tool
class DeribitGetContractSizeInput(BaseModel):
    """Input for DeribitGetContractSize tool."""

    instrument_name: str = Field(
        ...,
        description="Instrument name (e.g., BTC-PERPETUAL) (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first).",
    )


# DeribitGetContractSize tool to fetch contract size from Deribit API
class DeribitGetContractSize(DeribitBaseTool):
    """Tool to retrieve the contract size for a given instrument from Deribit API."""

    name: str = "get_contract_size"
    description: str = "Retrieves contract size of provided instrument."
    args_schema: Type[BaseModel] = DeribitGetContractSizeInput

    async def _arun(
        self,
        instrument_name: str,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is now str (CSV)
        """
        Fetch contract size for a specific instrument and return it as a CSV string.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "instrument_name": instrument_name,
            }

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/get_contract_size with params: {params}")
            raw_json = await self.api.get(
                "/api/v2/public/get_contract_size", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to CSV string using the utility
            formatted_result = format_json_result(raw_json, GetContractSizeResponse)
            logger.info(
                f"Successfully fetched contract size for {instrument_name} and format the result"
            )
            return formatted_result

        except Exception as e:
            logger.error(f"Error getting contract size for {instrument_name}: {str(e)}")
            # Still raise the error, but the return type hint is str for the successful path
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get contract size for {instrument_name}. Reason: {e}"
            ) from e
