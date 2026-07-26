import requests

def fetch_pools():
    response = requests.get("https://yields.llama.fi/pools")
    response.raise_for_status()
    return response.json()["data"]

def filter_pools(pools, chain=None, min_tvl_usd=0, stablecoin_only=False, top_n=5):
    filtered = pools

    if chain:
        filtered = [p for p in filtered if p["chain"].lower() == chain.lower()]

    filtered = [p for p in filtered if p["tvlUsd"] >= min_tvl_usd]

    if stablecoin_only:
        filtered = [p for p in filtered if p["stablecoin"]]

    filtered = sorted(filtered, key=lambda p: p["apy"], reverse=True)
    return filtered[:top_n]

from langchain_core.tools import tool

@tool
def get_top_yields(chain: str | None = None, min_tvl_usd: float = 0, stablecoin_only: bool = False, top_n: int = 5) -> list[dict]:
    """
    Get the top DeFi yield pools ranked by APY.

    Args:
        chain: filter by blockchain name, e.g. "Ethereum", "Arbitrum". None = all chains.
        min_tvl_usd: minimum total value locked in USD to include a pool.
        stablecoin_only: if True, only return stablecoin pools.
        top_n: how many top pools to return.
    """
    pools = fetch_pools()
    return filter_pools(pools, chain=chain, min_tvl_usd=min_tvl_usd, stablecoin_only=stablecoin_only, top_n=top_n)
