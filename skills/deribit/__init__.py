import logging
from typing import Literal, Optional, TypedDict

from abstracts.skill import SkillStoreABC
from skills.base import SkillConfig, SkillState
from skills.deribit.api import DeribitApi
from skills.deribit.base import DeribitBaseTool
from skills.deribit.market_data.get_book_summary_by_currency import (
    DeribitGetBookSummaryByCurrencyTool,
)
from skills.deribit.market_data.get_book_summary_by_instrument import (
    DeribitGetBookSummaryByInstrumentTool,
)
from skills.deribit.market_data.get_contract_size import DeribitGetContractSize
from skills.deribit.market_data.get_currencies import DeribitGetCurrencies
from skills.deribit.market_data.get_delivery_prices import DeribitGetDeliveryPrices
from skills.deribit.market_data.get_expirations import DeribitGetExpirationsTool
from skills.deribit.market_data.get_funding_chart_data import DeribitGetFundingChartData
from skills.deribit.market_data.get_funding_rate_history import (
    DeribitGetFundingRateHistory,
)
from skills.deribit.market_data.get_funding_rate_value import (
    DeribitGetFundingRateValueTool,
)
from skills.deribit.market_data.get_historical_volatility import (
    DeribitGetHistoricalVolatilityTool,
)
from skills.deribit.market_data.get_index import DeribitGetIndex
from skills.deribit.market_data.get_index_price import DeribitGetIndexPriceTool
from skills.deribit.market_data.get_index_price_names import DeribitGetIndexPriceNames
from skills.deribit.market_data.get_instrument import DeribitGetInstrument
from skills.deribit.market_data.get_instruments import DeribitGetInstrumentsTool
from skills.deribit.market_data.get_last_settlements_by_currency import (
    DeribitGetLastSettlementsByCurrency,
)
from skills.deribit.market_data.get_last_settlements_by_instrument import (
    DeribitGetLastSettlementsByInstrument,
)
from skills.deribit.market_data.get_last_trades_by_currency import (
    DeribitGetLastTradesByCurrency,
)
from skills.deribit.market_data.get_last_trades_by_currency_and_time import (
    DeribitGetLastTradesByCurrencyAndTimeTool,
)
from skills.deribit.market_data.get_last_trades_by_instrument import (
    DeribitGetLastTradesByInstrumentTool,
)
from skills.deribit.market_data.get_last_trades_by_instrument_and_time import (
    DeribitGetLastTradesByInstrumentAndTime,
)
from skills.deribit.market_data.get_mark_price_history import (
    DeribitGetMarkPriceHistoryTool,
)
from skills.deribit.market_data.get_order_book import DeribitGetOrderBookTool
from skills.deribit.market_data.get_order_book_by_instrument_id import (
    DeribitGetOrderBookByInstrumentIdTool,
)
from skills.deribit.market_data.get_rfqs import DeribitGetRFQs
from skills.deribit.market_data.get_supported_index_names import (
    DeribitGetSupportedIndexNames,
)
from skills.deribit.market_data.get_ticker import DeribitGetTicker
from skills.deribit.market_data.get_trade_volumes import DeribitGetTradeVolumes
from skills.deribit.market_data.get_tradingview_chart_data import (
    DeribitGetTradingviewChartData,
)
from skills.deribit.market_data.get_volatility_index_data import (
    DeribitGetVolatilityIndexDataTool,
)
from skills.deribit.supporting.get_time import DeribitGetTime
from skills.deribit.supporting.status import DeribitStatus
from skills.deribit.supporting.test import DeribitTest

# Cache skills at the system level, because they are stateless
_cache: dict[str, DeribitBaseTool] = {}

logger = logging.getLogger(__name__)


class SkillStates(TypedDict):
    get_book_summary_by_currency: SkillState
    get_book_summary_by_instrument: SkillState
    get_expirations: SkillState
    get_funding_rate_value: SkillState
    get_index_price: SkillState
    get_instruments: SkillState
    get_last_trades_by_currency_and_time: SkillState
    get_last_trades_by_instrument: SkillState
    get_mark_price_history: SkillState
    get_order_book_by_instrument_id: SkillState
    get_order_book: SkillState
    get_volatility_index_data: SkillState
    get_contract_size: SkillState
    get_currencies: SkillState
    get_delivery_prices: SkillState
    get_funding_chart_data: SkillState
    get_funding_rate_history: SkillState
    get_historical_volatility: SkillState
    get_index_price_names: SkillState
    get_index: SkillState
    get_instrument: SkillState
    get_last_settlements_by_currency: SkillState
    get_last_settlements_by_instrument: SkillState
    get_last_trades_by_currency: SkillState
    get_last_trades_by_instrument_and_time: SkillState
    get_rfqs: SkillState
    get_supported_index_names: SkillState
    get_ticker: SkillState
    get_trade_volumes: SkillState
    get_tradingview_chart_data: SkillState
    get_time: SkillState
    test: SkillState
    status: SkillState


_SKILL_NAME_TO_CLASS_MAP: dict[str, type[DeribitBaseTool]] = {
    "get_book_summary_by_currency": DeribitGetBookSummaryByCurrencyTool,
    "get_book_summary_by_instrument": DeribitGetBookSummaryByInstrumentTool,
    "get_expirations": DeribitGetExpirationsTool,
    "get_funding_rate_value": DeribitGetFundingRateValueTool,
    "get_historical_volatility": DeribitGetHistoricalVolatilityTool,
    "get_index_price": DeribitGetIndexPriceTool,
    "get_instruments": DeribitGetInstrumentsTool,
    "get_last_trades_by_currency_and_time": DeribitGetLastTradesByCurrencyAndTimeTool,
    "get_last_trades_by_instrument": DeribitGetLastTradesByInstrumentTool,
    "get_mark_price_history": DeribitGetMarkPriceHistoryTool,
    "get_order_book_by_instrument_id": DeribitGetOrderBookByInstrumentIdTool,
    "get_order_book": DeribitGetOrderBookTool,
    "get_volatility_index_data": DeribitGetVolatilityIndexDataTool,
    "get_contract_size": DeribitGetContractSize,
    "get_currencies": DeribitGetCurrencies,
    "get_delivery_prices": DeribitGetDeliveryPrices,
    "get_funding_chart_data": DeribitGetFundingChartData,
    "get_funding_rate_history": DeribitGetFundingRateHistory,
    "get_index_price_names": DeribitGetIndexPriceNames,
    "get_index": DeribitGetIndex,
    "get_instrument": DeribitGetInstrument,
    "get_last_settlements_by_currency": DeribitGetLastSettlementsByCurrency,
    "get_last_settlements_by_instrument": DeribitGetLastSettlementsByInstrument,
    "get_last_trades_by_currency": DeribitGetLastTradesByCurrency,
    "get_last_trades_by_instrument_and_time": DeribitGetLastTradesByInstrumentAndTime,
    "get_rfqs": DeribitGetRFQs,
    "get_supported_index_names": DeribitGetSupportedIndexNames,
    "get_ticker": DeribitGetTicker,
    "get_trade_volumes": DeribitGetTradeVolumes,
    "get_tradingview_chart_data": DeribitGetTradingviewChartData,
    "get_time": DeribitGetTime,
    "test": DeribitTest,
    "status": DeribitStatus,
}


class Config(SkillConfig):
    """Configuration for Deribit skills."""

    states: SkillStates
    client_id: str
    client_secret: str
    environment: Literal["production", "development"]


async def get_skills(
    config: "Config",
    is_private: bool,
    store: SkillStoreABC,
    **_,
) -> list[DeribitBaseTool]:
    """Get all Deribit skills.

    Args:
        config: The configuration for Deribit skills.
        is_private: Whether to include private skills.
        store: The skill store for persisting data.

    Returns:
        A list of Deribit skills.
    """
    available_skills = []

    client_id = config["client_id"]
    client_secret = config["client_secret"]

    base_url = ""

    if config["environment"] == "production":
        base_url = "https://www.deribit.com"
    else:
        base_url = "https://test.deribit.com"

    logger.debug(f"DERIBIT CLIENT_ID{client_id},CLIENT_SECRET {client_secret}")

    auth_service = DeribitApi(
        client_id=client_id, client_secret=client_secret, base_url=base_url
    )

    # Include skills based on their state
    for skill_name, state in config["states"].items():
        if state == "disabled":
            continue
        elif state == "public" or (state == "private" and is_private):
            available_skills.append(skill_name)

    # Get each skill using the cached getter

    result = []
    for name in available_skills:
        skill = get_deribit_skills(name, store, auth_service)
        if skill:
            result.append(skill)
    return result


def get_deribit_skills(
    name: str,
    store: SkillStoreABC,
    api: DeribitApi,
) -> Optional[DeribitBaseTool]:
    """Get a Deribit skill by name.

    Args:
        name: The name of the skill to get
        store: The skill store for persisting data

    Returns:
        The requested Deribit skill
    """

    # Return from cache immediately if already exists
    if name in _cache:
        return _cache[name]

    skill_class = _SKILL_NAME_TO_CLASS_MAP.get(name)
    if not skill_class:
        logger.warning(f"Unknown Venice skill: {name}")
        return None

    # Cache and return the newly created instance
    _cache[name] = skill_class(skill_store=store, api=api)
    return _cache[name]
