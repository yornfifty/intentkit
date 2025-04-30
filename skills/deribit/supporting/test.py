import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

# Updated import path for base tool
from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.supporting.response.test_response import (
    TestResponse,
)

# Updated import path for the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitTest tool
class DeribitTestInput(BaseModel):
    """Input for DeribitTest tool."""

    pass


# DeribitTest tool to test API connection and get version from Deribit API
class DeribitTest(DeribitBaseTool):
    """
    Tool to test the connection to the Deribit API server and return its version.
    Only call this tool if other API calls are failing unexpectedly, to check connectivity.
    """

    name: str = "test"
    description: str = (
        "Tests the connection to the API server and returns its version. "
        "Call this ONLY if other tools fail unexpectedly to diagnose connection issues."
    )
    args_schema: Type[BaseModel] = DeribitTestInput

    async def _arun(
        self,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result or error message)
        """
        Test the API connection, get the version, and return the formatted result.
        Can optionally trigger a test exception from the API.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit (less critical, but keep for consistency)
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {}
            # if expected_result is not None:
            #     params["expected_result"] = expected_result

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/test with params: {params}")
            # Note: self.api.get should handle the expected exception if triggered
            raw_json = await self.api.get("/api/v2/public/test", params=params)
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result (only reached if no exception)
            formatted_output = format_json_result(raw_json, TestResponse)
            logger.info("Successfully tested API connection and format the result")
            return formatted_output

        except Exception as e:
            # If expected_result was 'exception', the error is expected.
            # Otherwise, it's a real error.
            logger.error(f"Error testing API connection: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to test API connection. Reason: {e}"
            ) from e
