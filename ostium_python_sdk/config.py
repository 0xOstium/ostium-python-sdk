from dataclasses import dataclass
from typing import Dict, Optional


class NetworkConfig:
    def __init__(
        self,
        graph_url: str,
        contracts: Dict[str, str],
        is_testnet: bool
    ):
        self.graph_url = graph_url
        self.contracts = contracts
        self.is_testnet = is_testnet
        self.network = "testnet" if is_testnet else "mainnet"

    @classmethod
    def mainnet(cls) -> 'NetworkConfig':
        return cls(
            graph_url="https://subgraph.satsuma-prod.com/391a61815d32/ostium/ost-prod/api",
            contracts={
                "usdc": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
                "trading": "0x6D0bA1f9996DBD8885827e1b2e8f6593e7702411",
                "tradingStorage": "0xcCd5891083A8acD2074690F65d3024E7D13d66E7",
                "vault": "0x20D419a8e12C45f88fDA7c5760bb6923Cee27F98"
            },
            is_testnet=False
        )

    @classmethod
    def testnet(cls) -> 'NetworkConfig':
        return cls(
            graph_url="https://subgraph.satsuma-prod.com/391a61815d32/ostium/ost-sep-final/api",
            contracts={
                "usdc": "0xe73B11Fb1e3eeEe8AF2a23079A4410Fe1B370548",
                "trading": "0x2A9B9c988393f46a2537B0ff11E98c2C15a95afe",
                "tradingStorage": "0x0b9F5243B29938668c9Cfbd7557A389EC7Ef88b8",
                "vault": "0x2fbf52c8769c5da05afee7853b12775461cD04d2"
            },
            is_testnet=True
        )
