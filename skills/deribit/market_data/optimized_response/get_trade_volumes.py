import json
from datetime import datetime


def optimize_get_trade_volume_response(json_data):
    """
    Transforms raw Deribit trading volume API data into an AI-friendly format.

    Args:
        json_data (str or dict): JSON string or dictionary from Deribit API response

    Returns:
        dict: AI-optimized data structure with added insights and context
    """
    # Handle both string and dict inputs
    if isinstance(json_data, str):
        api_response = json.loads(json_data)
    else:
        api_response = json_data

    # Extract result data
    trading_data = api_response.get("result", [])

    # Create AI-friendly structured format
    ai_ready_data = {
        "meta": {
            "source": "Deribit",
            "endpoint": "/public/get_trade_volumes",
            "timeframe": "24h",
            "dataType": "trading_volumes",
            "timestamp": datetime.now().isoformat(),
            "instrumentTypes": ["spot", "futures", "options_calls", "options_puts"],
        },
        "currencies": {},
        "marketInsights": {
            "optionsSentiment": {},
            "volumeDistribution": {},
            "dominantMarkets": {},
        },
    }

    # Process each currency
    for currency_data in trading_data:
        currency_code = currency_data.get("currency")

        # Extract volumes with defaults for missing data
        spot_vol = currency_data.get("spot_volume", 0)
        futures_vol = currency_data.get("futures_volume", 0)
        calls_vol = currency_data.get("calls_volume", 0)
        puts_vol = currency_data.get("puts_volume", 0)

        # Calculate derived metrics
        total_options = puts_vol + calls_vol
        total_volume = spot_vol + futures_vol + total_options

        # Avoid division by zero
        put_call_ratio = puts_vol / calls_vol if calls_vol > 0 else float("inf")
        derivatives_ratio = (
            (futures_vol + total_options) / spot_vol if spot_vol > 0 else float("inf")
        )

        # Store processed currency data
        ai_ready_data["currencies"][currency_code] = {
            "volumes": {
                "spot": spot_vol,
                "futures": futures_vol,
                "options": {
                    "calls": calls_vol,
                    "puts": puts_vol,
                    "total": total_options,
                },
                "total": total_volume,
            },
            "distribution": {
                "spot": round(spot_vol / total_volume * 100, 1)
                if total_volume > 0
                else 0,
                "futures": round(futures_vol / total_volume * 100, 1)
                if total_volume > 0
                else 0,
                "options": {
                    "calls": round(calls_vol / total_volume * 100, 1)
                    if total_volume > 0
                    else 0,
                    "puts": round(puts_vol / total_volume * 100, 1)
                    if total_volume > 0
                    else 0,
                    "total": round((calls_vol + puts_vol) / total_volume * 100, 1)
                    if total_volume > 0
                    else 0,
                },
            },
            "insights": {
                "putCallRatio": round(put_call_ratio, 2)
                if put_call_ratio != float("inf")
                else None,
                "derivativesRatio": round(derivatives_ratio, 2)
                if derivatives_ratio != float("inf")
                else None,
                "dominantMarket": get_dominant_market(currency_data),
            },
        }

        # Add to market insights
        ai_ready_data["marketInsights"]["optionsSentiment"][currency_code] = (
            interpret_put_call_ratio(put_call_ratio)
        )
        ai_ready_data["marketInsights"]["volumeDistribution"][currency_code] = (
            get_volume_distribution(currency_data)
        )
        ai_ready_data["marketInsights"]["dominantMarkets"][currency_code] = (
            get_dominant_market(currency_data)
        )

    # Add vector representation (normalized volumes)
    ai_ready_data["vectorData"] = []
    for item in trading_data:
        spot_vol = item.get("spot_volume", 0)
        futures_vol = item.get("futures_volume", 0)
        calls_vol = item.get("calls_volume", 0)
        puts_vol = item.get("puts_volume", 0)

        total = spot_vol + futures_vol + calls_vol + puts_vol

        if total > 0:
            ai_ready_data["vectorData"].append(
                {
                    "currency": item.get("currency"),
                    "normalizedVolumes": [
                        spot_vol / total,
                        futures_vol / total,
                        calls_vol / total,
                        puts_vol / total,
                    ],
                }
            )

    # Include extended timeframe data if available (7d/30d)
    if any(
        "_7d" in key or "_30d" in key for item in trading_data for key in item.keys()
    ):
        ai_ready_data["meta"]["timeframes"] = ["24h", "7d", "30d"]

        for currency_data in trading_data:
            currency_code = currency_data.get("currency")
            if currency_code in ai_ready_data["currencies"]:
                # Add 7d data if available
                if any(key.endswith("_7d") for key in currency_data.keys()):
                    ai_ready_data["currencies"][currency_code]["volumes_7d"] = {
                        "spot": currency_data.get("spot_volume_7d", 0),
                        "futures": currency_data.get("futures_volume_7d", 0),
                        "options": {
                            "calls": currency_data.get("calls_volume_7d", 0),
                            "puts": currency_data.get("puts_volume_7d", 0),
                            "total": currency_data.get("calls_volume_7d", 0)
                            + currency_data.get("puts_volume_7d", 0),
                        },
                    }

                # Add 30d data if available
                if any(key.endswith("_30d") for key in currency_data.keys()):
                    ai_ready_data["currencies"][currency_code]["volumes_30d"] = {
                        "spot": currency_data.get("spot_volume_30d", 0),
                        "futures": currency_data.get("futures_volume_30d", 0),
                        "options": {
                            "calls": currency_data.get("calls_volume_30d", 0),
                            "puts": currency_data.get("puts_volume_30d", 0),
                            "total": currency_data.get("calls_volume_30d", 0)
                            + currency_data.get("puts_volume_30d", 0),
                        },
                    }

    return ai_ready_data


def interpret_put_call_ratio(ratio):
    """Interpret the put/call ratio as a market sentiment indicator"""
    if ratio == float("inf"):  # No calls
        return "extremely_bearish"
    if ratio > 1.5:
        return "bearish"
    if ratio > 1.0:
        return "slightly_bearish"
    if ratio > 0.7:
        return "neutral"
    if ratio > 0.4:
        return "slightly_bullish"
    return "bullish"


def get_volume_distribution(currency_data):
    """Analyze if trading volume is balanced across instruments or concentrated"""
    spot_vol = currency_data.get("spot_volume", 0)
    futures_vol = currency_data.get("futures_volume", 0)
    calls_vol = currency_data.get("calls_volume", 0)
    puts_vol = currency_data.get("puts_volume", 0)

    total = spot_vol + futures_vol + calls_vol + puts_vol

    if total == 0:
        return "no_data"

    # Calculate proportions
    volumes = [
        spot_vol / total,
        futures_vol / total,
        calls_vol / total,
        puts_vol / total,
    ]

    # Determine if volume is balanced or concentrated
    max_proportion = max(volumes)
    if max_proportion > 0.6:
        return "highly_concentrated"
    if max_proportion > 0.4:
        return "concentrated"
    return "balanced"


def get_dominant_market(currency_data):
    """Identify which market has the highest trading volume"""
    markets = [
        {"name": "spot", "value": currency_data.get("spot_volume", 0)},
        {"name": "futures", "value": currency_data.get("futures_volume", 0)},
        {"name": "calls", "value": currency_data.get("calls_volume", 0)},
        {"name": "puts", "value": currency_data.get("puts_volume", 0)},
    ]

    # Sort by value in descending order
    markets.sort(key=lambda x: x["value"], reverse=True)
    return markets[0]["name"]


# Example usage
if __name__ == "__main__":
    # Sample data from Deribit API
    sample_data = {
        "jsonrpc": "2.0",
        "id": 6387,
        "result": [
            {
                "puts_volume": 48,
                "futures_volume": 6.25578452,
                "currency": "BTC",
                "calls_volume": 145,
                "spot_volume": 11.1,
            },
            {
                "puts_volume": 122.65,
                "futures_volume": 374.392173,
                "currency": "ETH",
                "calls_volume": 37.4,
                "spot_volume": 57.7,
            },
        ],
    }

    # Process the data
    optimized_data = optimize_get_trade_volume_response(sample_data)

    # Print the result
    print(json.dumps(optimized_data, indent=2))
