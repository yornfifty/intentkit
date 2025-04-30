import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool
from skills.deribit.market_data.response.get_index_price_response import (
    GetIndexPriceResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)

# List of available index names
INDEX_OPTION = [
    "ada_usd",
    "algo_usd",
    "avax_usd",
    "bch_usd",
    "btc_usd",
    "doge_usd",
    "dot_usd",
    "eth_usd",
    "link_usd",
    "ltc_usd",
    "matic_usd",
    "near_usd",
    "shib_usd",
    "sol_usd",
    "steth_usd",
    "trx_usd",
    "uni_usd",
    "usdc_usd",
    "xrp_usd",
    "paxg_usd",
    "usde_usd",
    "ada_usdc",
    "bch_usdc",
    "algo_usdc",
    "avax_usdc",
    "btc_usdc",
    "doge_usdc",
    "dot_usdc",
    "eth_usdc",
    "link_usdc",
    "ltc_usdc",
    "matic_usdc",
    "near_usdc",
    "shib_usdc",
    "sol_usdc",
    "steth_usdc",
    "trx_usdc",
    "usyc_usdc",
    "uni_usdc",
    "xrp_usdc",
    "paxg_usdc",
    "usde_usdc",
    "ada_usdt",
    "algo_usdt",
    "avax_usdt",
    "bch_usdt",
    "bnb_usdt",
    "btc_usdt",
    "doge_usdt",
    "dot_usdt",
    "eth_usdt",
    "link_usdt",
    "ltc_usdt",
    "luna_usdt",
    "matic_usdt",
    "near_usdt",
    "shib_usdt",
    "sol_usdt",
    "steth_usdt",
    "trx_usdt",
    "uni_usdt",
    "xrp_usdt",
    "paxg_usdt",
    "usde_usdt",
    "btcdvol_usdc",
    "ethdvol_usdc",
    "steth_eth",
    "paxg_btc",
    "btc_usyc",
    "eth_usyc",
    "btc_usde",
    "eth_usde",
]


class DeribitGetIndexPriceInput(BaseModel):
    """Input for DeribitGetIndexPrice tool."""

    index_name: str = Field(
        ...,
        description=f"Index identifier. Available options: {', '.join(INDEX_OPTION)}",
    )


# DeribitGetIndexPrice tool to fetch index price from Deribit API
class DeribitGetIndexPriceTool(DeribitBaseTool):
    """Tool to retrieve the current index price value for a given index name from Deribit API."""

    name: str = "get_index_price"
    description: str = "Retrieves the current index price value for a given index name."
    args_schema: Type[BaseModel] = DeribitGetIndexPriceInput

    async def _arun(
        self,
        index_name: str,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch the current index price for a specific index name.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {"index_name": index_name}

            logger.debug(f"Calling /public/get_index_price with params: {params}")
            raw_json = await self.api.get(
                "/api/v2/public/get_index_price", params=params
            )
            return format_json_result(raw_json, GetIndexPriceResponse)

        except Exception as e:
            logger.error(f"Error getting index price for {index_name}: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get index price for {index_name}. Reason: {e}"
            ) from e
