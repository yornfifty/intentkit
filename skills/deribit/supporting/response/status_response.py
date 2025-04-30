from typing import List, Literal, Optional

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for the 'result' object ---
class StatusResult(BaseModel):
    """Result object containing platform lock status."""

    # Description says string literal, example shows boolean. Following description.
    locked: Literal["true", "partial", "false"] = Field(
        description="true when platform is locked in all currencies, partial when some are locked, false when none are locked."
    )
    # Description says 'locked_indices', example shows 'locked_currencies'. Using description name with alias.
    locked_indices: Optional[List[str]] = (
        Field(  # Optional as it might be empty/null if locked=false
            default=None,
            alias="locked_currencies",
            description="List of currency symbols locked platform-wise.",
        )
    )

    # Allow population by alias for locked_currencies -> locked_indices
    model_config = {"populate_by_name": True}


# --- Main Response Model ---
class StatusResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/status endpoint.
    Parsing and validation happen during instantiation.
    """

    result: StatusResult = Field(
        description="Contains the platform lock status information."
    )
