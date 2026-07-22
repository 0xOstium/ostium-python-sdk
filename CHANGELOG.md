# Changelog

All notable changes to the Ostium Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.1] - 2026-07-21

### Changed
- Migrated price feed endpoint to `metadata-backend.prod.bedrock.ostium.io`

## [3.3.0] - 2026-07-09

### Performance
- **Transactions are broadcast through the Arbitrum sequencer feed by default** (`https://arb1-sequencer.arbitrum.io/rpc` on mainnet, the Sepolia feed on testnet), while all reads and receipt polling stay on the primary RPC. Median broadcast time dropped from ~980ms (third-party RPC) to ~700ms. Configurable: pass `submit_rpc_url` to `OstiumSDK`/`Ostium`, or call `ostium.set_submit_rpc_url(url)` (pass your primary RPC URL to disable the split; `None` restores the sequencer default). If the submit endpoint errors, the SDK automatically falls back to the primary RPC.
- **`track_order_and_trade` now watches the chain instead of polling the subgraph.** Order settlement is detected via the callbacks contract's events (`MarketOpenExecuted`, `MarketCloseExecutedV2`, cancellations, …) with a single `eth_getLogs` filter on the indexed orderId — the oracle settles orders in ~1s and each poll costs ~90ms, vs 12–14s total with subgraph polling (0.6–1.7s per query plus ~10s indexing lag). After settlement the subgraph is tried once for the enriched payload; if not yet indexed, a result built from the settlement event is returned (same shape, `order['source'] == 'chain'`, subset of fields). Legacy subgraph polling remains as automatic fallback when on-chain tracking is unavailable. Accepts an optional `from_block` (e.g. the send receipt's `blockNumber`). The callbacks contract address is resolved at runtime through the on-chain registry.
- **Transactions are now built offline.** `chainId` (validated once at SDK init), a static gas ceiling and static fee caps are supplied to every `build_transaction` call, eliminating ~7 sequential JSON-RPC round-trips per trade (`eth_chainId` ×3, `eth_estimateGas`, fee-history lookups, duplicate nonce fetch). Measured pre-send latency for `perform_trade()`: 5.7s → 0.7s on a public Arbitrum RPC; 1.2s → ~0.6s on a dedicated RPC. Calldata is byte-identical to previous versions.
- **Nonce and USDC allowance are fetched concurrently** in `perform_trade()`, and the allowance is cached per trader after the first check (re-fetched only when the cached value can no longer cover a trade).
- **Delegation calldata is encoded locally** via `encodeABI` instead of `build_transaction({'gas': 0})`, removing all RPC calls from inner-call encoding on every delegated operation.
- **Subgraph client no longer downloads the GraphQL schema** on first use (`fetch_schema_from_transport=False`), saving ~2.5s on the first subgraph query of every session.

### Changed
- **All bundled ABIs refreshed from the verified on-chain implementation contracts** (trading, tradingStorage, USDC, pairInfos, pairsStorage, vault — addresses resolved via the Ostium registry `0x799a139aE56e11F0476aCE2f6118CfcAed9608d2`). Calldata for every SDK write function verified byte-identical before/after. The testnet faucet ABI is unchanged (contract not verified on Blockscout).

### Added
- `Ostium` accepts an optional `chain_id` constructor parameter (passed automatically by `OstiumSDK`; lazily fetched from the RPC when constructed standalone).
- Configurable transaction gas parameters on `Ostium`: `gas_limit` (default 2,500,000 — an upper bound, Arbitrum refunds unused gas), `max_fee_per_gas` (default 0.5 gwei — a cap, the actual charge is the network base fee) and `max_priority_fee_per_gas` (default 0).

### Fixed
- **`order_id` extraction from trade receipts.** The oracle contract replaced `PriceRequested(uint256,bytes32,uint256)` with `PriceRequestedV2(uint256,uint8,bytes32,uint256)`, so `perform_trade()`/`close_trade()` returned `order_id=None` and `track_order_and_trade()` raised `ValueError`. Order IDs are now extracted from `PriceRequestedV2`, with the trading contract's `MarketOpenOrderInitiated` / `MarketCloseOrderInitiatedV2` events as fallback. Verified with live mainnet trades.

### Notes
- Gas is no longer estimated per transaction via `eth_estimateGas`. A transaction that would revert now fails on-chain rather than at estimation time; the SDK's existing error decoding still surfaces the revert reason from the receipt/require string.

## [3.2.0] - 2026-04-28

> **Release timing:** Upgrade to `3.2.0` on **Apr 28 after 9:00 AM EST**, when the contract upgrade is live.  
> Upgrading earlier may prevent opening new trades, and staying on an older version after go-live may also prevent opening new trades.

### Breaking Changes
- **`openTrade` contract upgrade: `isDayTrade` field added to the `Trade` struct.** The `perform_trade()` method now accepts an optional `is_day_trade` parameter (default: `False`).

### Added
- `is_day_trade` parameter in `perform_trade()` via `trade_params['is_day_trade']` (defaults to `False`)

### Migration Guide
- For most pairs (`overnightMaxLeverage === 0`, e.g. crypto, forex, commodities) no changes are needed — `isDayTrade` defaults to `False` and is safely ignored by the contract.
- For stock pairs where `overnightMaxLeverage > 0`, set `is_day_trade=True` when the trade's leverage exceeds `overnightMaxLeverage`. Note that such trades will be **auto-closed before market close**.
- Use the subgraph method `get_pair_details(pair_id)` to read `overnightMaxLeverage` for a given pair.

```python
# For crypto/forex/commodities — no change needed (default False)
trade_params = { ..., 'is_day_trade': False }

# For stock pairs, when the desired leverage exceeds overnightMaxLeverage, set is_day_trade=True:
trade_params = { ..., 'is_day_trade': True }  # trade will auto-close before market close
```

## [3.1.0] - 2026-02-14

### Breaking Changes
- **Limit and Stop orders now enforce slippage = 0** per contract upgrade. Slippage is no longer configurable for LIMIT/STOP order types and is hardcoded to 0. Market orders are unaffected.

### Changed
- Migrated subgraph URLs to new Ormi Labs hosted endpoints for both mainnet and testnet
- `perform_trade()` now sets slippage to 0 for LIMIT and STOP orders regardless of `set_slippage_percentage()` value

## [3.0.0] - 2025-10-15

### Breaking Changes
- **IMPORTANT**: Updated to support new Ostium Protocol contract upgrade
- `perform_trade()` now includes BuilderFee parameter in contract calls
- `close_trade()` now requires `market_price` parameter and includes slippage protection

### Added
- Builder fee support in `perform_trade()` via optional `builder_address` and `builder_fee` parameters
- Market price parameter in `close_trade()` for accurate slippage calculation
- Automatic slippage protection when closing trades
- New `close_timeout()` method to handle timed out close market orders (retry or cancel)
- New `open_market_timeout()` method to execute timed out open market orders
- New test suite for builder fee functionality

### Changed
- `close_trade()` signature now requires `market_price` as third parameter
- Contract calls now use updated ABI with BuilderFee struct for `openTrade`
- Contract calls now use updated ABI with market price and slippage for `closeTradeMarket`

### Migration Guide
- For `perform_trade()`: No changes needed if not using builder fees (defaults to zero)
- For `close_trade()`: Must now provide current market price as third parameter
  ```python
  # Old: sdk.ostium.close_trade(pair_id, trade_index, close_percentage)
  # New: sdk.ostium.close_trade(pair_id, trade_index, market_price, close_percentage)
  ```
- New timeout handling methods for managing timed out orders:
  ```python
  # Handle a timed out close order
  sdk.ostium.close_timeout(order_id, retry=True)  # Retry the close
  sdk.ostium.close_timeout(order_id, retry=False) # Cancel the close
  
  # Execute a timed out open order
  sdk.ostium.open_market_timeout(order_id)  # Execute the open trade
  ```

## [2.0.18] - 2025-06-23

- Add delegate support for cancel_limit_order

## [2.0.17] - 2025-06-03

- Return target_funding_rate from getPendingAccFundingFees() 

## [2.0.16] - 2025-05-31

- query optional different address in sdk.get_open_trade_metrics()

## [2.0.15] - 2025-05-28

- Updated Readme with list of pairs
- Add additional fields to get_open_trade_metrics: bid, mid, ask, status

## [2.0.12] - 2025-05-28

- return isDayTradingClosed in sdk.get_formatted_pairs_details()

## [2.0.11] - 2025-05-28

- improve sdk.get_formatted_pairs_details()

## [2.0.10] - 2025-05-27

- Add sdk.get_target_funding_rate() for pair
- Fix Liquidiation price calculation
- Fix Funding Fee rate calculation
- Add get_pair_overnight_max_leverage() for pair

## [2.0.5] - 2025-05-26

- Support new ABIs from smart-contracts v.1.2.3: PairInfo, PairStorage, Trading, TradingStorage, Vault.
- Fix getTradeLiquidationPrice() exposed in sdk.get_open_trade_metrics()
- Allow get_open_trades() with an optional parameter trader_address
- Add sdk.get_rollover_rate_for_pair_id()

## [2.0.4] - 2025-05-26

### Added
- `track_order_and_trade` that let's you track an order status until its processed.
- Added support for delegation which allows an approved
  address (delegate) to execute trades on behalf of another address (trader).

## [2.0.3] - 2025-03-06

### Added
- `close_trade` that allows a partial close

## [2.0.2] - 2025-03-06

### Added
- `remove_collateral`


## [2.0.1] - 2025-03-05

### Added
- Validate RPC_URL given correspondes with mainnet/testnet


## [2.0.0] - 2025-03-04

Version 2.0

## [0.2.1] - 2025-02-21

### Added
- Added sdk method `get_pair_net_rate_percent_per_hours` to get net rate percent per hours for a given pair

## [0.2.0] - 2025-02-20

### Added

- Added sdk method `get_open_trade_metrics` to get open trade metrics such as:
  - Funding fee
  - Roll over fee
  - Unrealized Pnl and Pnl Percent
  - Total Profit
  - Liquidation Price 

- Added verbose mode to sdk (default is False, set to True to see debug logs)

## [0.1.36] - 2025-01-14

### Added
- Before write-operations, check if private key is provided

## [0.1.34] - 2025-01-14

### Added
- Allow read only operations on the SDK without providing a private key

## [0.1.31] - 2025-01-13

### Added
- Add `get_formatted_pairs_details` on sdk class

## [0.1.25] - 2025-01-13

### Added
- Custom slippage control functionality
  - New method `set_slippage_percentage()` to customize trade slippage
  - New method `get_slippage_percentage()` to check current slippage setting
  - Ability to set slippage beyond the default 2%
- add USDC faucet ability to sdk for testnet configuration
- Add trades history - `get_recent_history`
- Adding of Tests


## [0.1.0] - 2025-01-10

### Added
- Initial release of Ostium Python SDK
- Core trading functionality:
  - Market, limit, and stop orders
  - Position management (open, close, modify)
  - Take profit and stop loss settings
- Price feed integration
- Balance checking and management
- Testnet faucet integration
- Subgraph querying for market data
- Comprehensive documentation and examples 