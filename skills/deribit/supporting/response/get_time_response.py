from pydantic import Field

# Updated import path for base response relative to the new directory structure
from skills.deribit.base_response import DeribitBaseResponse


# --- Main Response Model ---
class GetTimeResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_time endpoint.
    The result is the current server time as a timestamp.
    Parsing and validation happen during instantiation.
    """

    result: int = Field(
        description="Current timestamp (milliseconds since the UNIX epoch)."
    )
