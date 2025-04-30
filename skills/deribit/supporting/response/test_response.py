from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for the 'result' object ---
class TestResult(BaseModel):
    """Result object containing the API version."""

    version: str = Field(description="The API version.")


# --- Main Response Model ---
class TestResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/test endpoint.
    Parsing and validation happen during instantiation.
    """

    result: TestResult = Field(description="Contains the API version.")
