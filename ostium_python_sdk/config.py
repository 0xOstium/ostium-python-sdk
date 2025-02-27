from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class NetworkConfig:
    graph_url: str
    contracts: Dict[str, str]
    is_testnet: bool = False

    @classmethod
    def mainnet(cls) -> 'NetworkConfig':
        return cls(
            graph_url="https://subgraph.satsuma-prod.com/391a61815d32/ostium/ost-prod/api",
            contracts={
                "usdc": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
                "trading": "0x6D0bA1f9996DBD8885827e1b2e8f6593e7702411",
                "tradingStorage": "0xcCd5891083A8acD2074690F65d3024E7D13d66E7"
            },
            is_testnet=False
        )

    @classmethod
    def testnet(cls) -> 'NetworkConfig':
        return cls(  # tbd


            graph_url="https://subgraph.satsuma-prod.com/391a61815d32/ostium/ost-sep-final/api",
            contracts={
                "usdc": "0xe73B11Fb1e3eeEe8AF2a23079A4410Fe1B370548",
                "trading": "0x2A9B9c988393f46a2537B0ff11E98c2C15a95afe",
                "tradingStorage": "0x0b9F5243B29938668c9Cfbd7557A389EC7Ef88b8"
            },
            is_testnet=True
        )
