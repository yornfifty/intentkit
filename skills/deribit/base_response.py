from typing import Optional

from pydantic import BaseModel, Field


class DeribitBaseResponse(BaseModel):
    """
    Base model for common fields found in successful Deribit JSON-RPC responses.
    Specific response models should inherit from this.
    """

    jsonrpc: Optional[str] = Field(default=None, description="The JSON-RPC version.")
    id: Optional[str] = Field(
        default=None, description="The identifier sent in the request."
    )
    # Optional common fields often included by Deribit
    usIn: Optional[int] = Field(
        default=None,
        description="Timestamp (microseconds) when the request entered Deribit.",
    )
    usOut: Optional[int] = Field(
        default=None,
        description="Timestamp (microseconds) when the response left Deribit.",
    )
    usDiff: Optional[int] = Field(
        default=None,
        description="Time difference (microseconds) between usOut and usIn.",
    )
    testnet: Optional[bool] = Field(
        default=None,
        description="Indicates if the response is from the testnet environment.",
    )

    # Note: The 'result' field is intentionally omitted here because its
    # type varies significantly between different API endpoints.
    # Subclasses will define their specific 'result' field.
