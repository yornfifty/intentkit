import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool
from skills.deribit.market_data.response.get_book_summary_by_currency_response import (
    GetBookSummaryByCurrencyResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetExpirations tool
class DeribitGetExpirationsInput(BaseModel):
    """Input for DeribitGetExpirations tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR", "any"] = Field(
        ..., description="Currency symbol (BTC, ETH, USDC, USDT, EURR, or 'any')"
    )
    kind: Literal["future", "option", "any"] = Field(
        ..., description="Instrument kind: future, option, or any"
    )
    currency_pair: Optional[str] = Field(
        None,
        description=(
            "Currency pair symbol (optional). Available pairs include:\n"
            "ada_usd, algo_usd, avax_usd, bch_usd, btc_usd, doge_usd, dot_usd, "
            "eth_usd, link_usd, ltc_usd, matic_usd, near_usd, shib_usd, sol_usd, "
            "steth_usd, trx_usd, uni_usd, xrp_usd, paxg_usd, usde_usd, ada_usdc, "
            "bch_usdc, algo_usdc, avax_usdc, btc_usdc, doge_usdc, dot_usdc, eth_usdc, "
            "link_usdc, ltc_usdc, matic_usdc, near_usdc, shib_usdc, sol_usdc, "
            "steth_usdc, trx_usdc, usyc_usdc, uni_usdc, xrp_usdc, paxg_usdc, "
            "usde_usdc, ada_usdt, algo_usdt, avax_usdt, bch_usdt, bnb_usdt, btc_usdt, "
            "doge_usdt, dot_usdt, eth_usdt, link_usdt, ltc_usdt, luna_usdt, matic_usdt, "
            "near_usdt, shib_usdt, sol_usdt, steth_usdt, trx_usdt, uni_usdt, xrp_usdt, "
            "paxg_usdt, usde_usdt, btcdvol_usdc, ethdvol_usdc, steth_eth, paxg_btc, "
            "btc_usyc, eth_usyc, btc_usde, eth_usde"
        ),
    )


# DeribitGetExpirations tool to fetch expirations from Deribit API
class DeribitGetExpirationsTool(DeribitBaseTool):
    """Tool to fetch expirations of instruments from Deribit API."""

    name: str = "get_expirations"
    description: str = "Get expirations for available instruments from Deribit."
    args_schema: Type[BaseModel] = DeribitGetExpirationsInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR", "any"],
        kind: Literal["future", "option", "any"],
        currency_pair: Optional[str] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch expirations for instruments from Deribit based on the provided parameters.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Call the API to get expirations
            params = {"currency": currency, "kind": kind}

            if currency_pair is not None:
                params["currency_pair"] = currency_pair

            raw_json = await self.api.get(
                "/api/v2/public/get_expirations", params=params
            )

            return format_json_result(raw_json, GetBookSummaryByCurrencyResponse)

        except Exception as e:
            logger.error("Error getting expirations: %s", str(e))
            raise type(e)(f"[agent:{context.agent.id}]: {e}") from e
