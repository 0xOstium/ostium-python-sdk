# Changelog
[![Changelog](https://img.shields.io/badge/changelog-View%20Latest%20Changes-blue.svg)](https://github.com/0xOstium/ostium-python-sdk/blob/main/CHANGELOG.md)

Track all notable changes, updates, and improvements to the Ostium Python SDK in our [Changelog](https://github.com/0xOstium/ostium-python-sdk/blob/main/CHANGELOG.md).

# Ostium Python SDK

A python based SDK developed for interacting with Ostium v1 Trading Platform (https://ostium.app/)

Ostium is a decentralized perpetuals exchange on Arbitrum (Ethereum L2) with a focus on providing a seamless experience for traders for trading currencies, commodities, indices, crypto and more.

This SDK is designed to be used by developers who want to build applications on top of Ostium and automate their trading strategies.

## Supported Operations

Basically you can perfrom any operation that is supported by the Ostium's web site in a programmatic way, via the SDK:

- Get list of feeds and their details
- Create a Trade/Order
- Close a Trade, Partial Close a trade, Set Take Profit, Set Stop Loss
- Add Colleteral, Remove Collateral
- Cancel an Order, Set Take Profit, Set Stop Loss, Set Entry Price
- Read Open Trades aka Positions
- Read Open Orders (Limit, Stop)
- Read Order History along with their details such as Pnl, etc.
- Get latest price of a feed
- Calculate fees such as funding rate, rollover fee, etc.
- Call testnet faucet to get testnet USDC tokens
- Read balance of your account, usdc and native token

You can check this repository - https://github.com/0xOstium/use-ostium-python-sdk for more examples of how to use the SDK. Its shows how to create orders, trade,
set tp/sl, cancel orders, get funding rate, rollover fee, percent profit/loss etc.

*To use the SDK you need to have a valid EVM private key for an account on either Arbitrum (mainnet) or Arbitrum Sepolia (testnet), depending on which network you plan to use and supply a RPC URL, see below for more details.*
## Installation

The SDK can be installed via pip:

```bash
pip install ostium-python-sdk
```

## Running Tests

First, install the package with development dependencies:

```bash
pip install -e ".[dev]"
```

## Running tests

### Run specific tests

```bash
pytest -v tests/test_trade_liquidation_price.py
pytest -v tests/test_funding.py
pytest -v tests/test_trade_get_tp_price.py
pytest -v tests/test_trade_get_sl_price.py
pytest -v tests/test_current_trade_profit_p.py
pytest -v tests/test_top_up_with_collateral.py
pytest -v tests/test_top_up_with_leverage.py
pytest -v tests/test_remove_collateral_with_collateral.py
pytest -v tests/test_remove_collateral_from_leverage.py
pytest -v tests/test_current_total_profit_p.py
pytest -v tests/test_current_trade_profit_raw.py
pytest -v tests/test_current_total_profit_raw.py
pytest -v tests/test_get_trade_funding_fee.py
pytest -v tests/test_get_trade_rollover_fee.py 
pytest -v tests/test_get_trade_value.py 
pytest -v tests/test_get_opening_fee.py 


pytest -v tests/test_get_pending_acc_funding_fees.py

pytest -v tests/test_max_leverage.py 
pytest -v tests/test_overnight_max_leverage.py 
pytest -v tests/test_slippage.py 
pytest -v tests/test_target_funding_rate.py 

pytest -v tests/test_vault.py 











```

### Run ALL tests
```bash
pytest
```

## Requirements

Developed using:
```python
  python=3.8
```
## SDK Instantiation 

You can instantiate the SDK with the following parameters. 
Ostium Platform is deployed on Arbitrum. You can use the testnet or mainnet config via the `NetworkConfig` class, see below for an example.

```python
from dotenv import load_dotenv
from ostium_python_sdk import OstiumSDK, NetworkConfig

# Load environment variables if using .env file
load_dotenv()

# Get private key from environment variable 
private_key = os.getenv('PRIVATE_KEY')
if not private_key:
    raise ValueError("PRIVATE_KEY not found in .env file")

rpc_url = os.getenv('RPC_URL')
if not rpc_url:
    raise ValueError("RPC_URL not found in .env file")

# Initialize SDK (default: verbose=False for quiet operation)
configTestnet = NetworkConfig.testnet()
sdk = OstiumSDK(configTestnet, private_key, rpc_url)

# For verbose mode with detailed logging:
sdk = OstiumSDK(configTestnet, private_key, rpc_url, verbose=True)
```

<b>NOTE:</b> create a .env file with PRIVATE_KEY and RPC_URL to use the SDK. An RPC URL is required to use the SDK. You can get one by signing up for a free account at https://www.alchemy.com/ and creating an app. 

**NOTE: You can also use the SDK _without_ providing a private key, in which case you will be limited to read only operations on the SDK.**

```
PRIVATE_KEY=your_private_key_here
RPC_URL=https://arb-sepolia.g.alchemy.com/v2/...
#RPC_URL="https://arb-mainnet.g.alchemy.com/v2/...",
```

`your_private_key_here` should be a valid EVM private key for an account on either Arbitrum (mainnet) or Arbitrum Sepolia (testnet), depending on which network you plan to use. 

**Make sure to save it in a secure location, and that the .env file is not shared with anyone or committed to a public repository (make sure you add it to .gitignore if you are pushing your code).**

## Testnet and Fuacet to get USDC tokens

As you can see above, we show use case on testnet. In order to use Ostium on testnet, aka on Arbitrum Sepolia, you need to get testnet USDC tokens. You can do this by using the faucet which is also available on the SDK once instantiated in testnet config.

```python
# Get current token amount from faucet
# On testnet
sdk = OstiumSDK(NetworkConfig.testnet(), private_key, rpc_url)

# Check if tokens can be requested
if sdk.faucet.can_request_tokens(address):
    # Get amount that will be received
    amount = sdk.faucet.get_token_amount()
    print(f"Will receive {amount} tokens")
    
    # Request tokens
    receipt = sdk.faucet.request_tokens()
    print(f"Tokens requested successfully! TX: {receipt['transactionHash'].hex()}")
else:
    next_time = sdk.faucet.get_next_request_time(address)
    print(f"Cannot request tokens yet. Next request allowed at: {next_time}")

```

![#f03c15](https://placehold.co/15x15/f03c15/f03c15.png) NOTE: You will also need gas aka ethereum or native token on Arbitrum Sepolia to even be able to request USDC tokens from the faucet or perform any write blockchain operation. You can get some native token for Arbitrum Sepolia for free at: https://www.alchemy.com/faucets/arbitrum-sepolia (or search for "arbitrum sepolia faucet")


## The SDK contains the following classes:

- `OstiumSDK`: The main class for interacting with the Ostium Platform.

- `NetworkConfig`: The class for configuring the network.

- `Balance`: The class for interacting with the account, fetching balance, etc. available via `sdk.balance`.

- `SubgraphClient`: The class for interacting with the subgraph, getting pair details, open trades, open orders,etc. available via `sdk.subgraph`.

- `Price`: The class for interacting with the price, fetching latest price, etc. available via `sdk.price`

- `Ostium`: The class for interacting with the Ostium Smart contracts, opening trades, updating take profit and stop loss, closing trades, opening orders, etc. available via `sdk.ostium`.

- `Faucet`: The class for interacting with the Faucet for getting testnet USDC tokens. available via `sdk.faucet`.

## Basic Usage

The intraction with Ostium platform is denoted with pair_id and trade_index. 

- `pair_id`: The id of the pair, available via `sdk.subgraph.get_pairs()`
- `trade_index`: The index of the trade for this trader on the pair, available via `sdk.subgraph.get_open_trades()`

## List of available pairs (Mainnet)

- As of May 2025, the following pairs are available on the mainnet: 

| ID | Trading Pair | Description                    |
|----|--------------|--------------------------------|
| 0  | BTC-USD      | Bitcoin                        |
| 1  | ETH-USD      | Ethereum                       |
| 2  | EUR-USD      | Euro                           |
| 3  | GBP-USD      | British Pound                  |
| 4  | USD-JPY      | US Dollar to Japanese Yen      |
| 5  | XAU-USD      | Gold                           |
| 6  | HG-USD       | Copper                         |
| 7  | CL-USD       | Crude Oil                      |
| 8  | XAG-USD      | Silver                         |
| 9  | SOL-USD      | Solana                         |
| 10 | SPX-USD      | S&P 500 Index                  |
| 11 | DJI-USD      | Dow Jones Industrial Average   |
| 12 | NDX-USD      | NASDAQ-100 Index               |
| 13 | NIK-JPY      | Nikkei 225 Index               |
| 14 | FTSE-GBP     | FTSE 100 Index                 |
| 15 | DAX-EUR      | DAX Index                      |
| 16 | USD-CAD      | US Dollar to Canadian Dollar   |
| 17 | USD-MXN      | US Dollar to Mexican Peso      |
| 18 | NVDA-USD     | NVIDIA Stock                   |
| 19 | GOOG-USD     | Alphabet (Google) Stock        |
| 20 | AMZN-USD     | Amazon Stock                   |
| 21 | META-USD     | Meta (Facebook) Stock          |
| 22 | TSLA-USD     | Tesla Stock                    |
| 23 | AAPL-USD     | Apple Stock                    |
| 24 | MSFT-USD     | Microsoft Stock                |

## Usage Examples

### Reading available pairs / feeds

```python
from ostium_python_sdk import OstiumSDK
from dotenv import load_dotenv

# Load environment variables if using .env file
load_dotenv()

# Get private key from environment variable
private_key = os.getenv('PRIVATE_KEY')
if not private_key:
    raise ValueError("PRIVATE_KEY not found in .env file")

rpc_url = os.getenv('RPC_URL')
if not rpc_url:
    raise ValueError("RPC_URL not found in .env file")

# Initialize SDK
config = NetworkConfig.testnet()
sdk = OstiumSDK(config, private_key, rpc_url)

# Or, initialize:
#
# (1) mainnet:
#
# config = NetworkConfig.mainnet()
# sdk = OstiumSDK(config, private_key, rpc_url)
# 
# (2) with explicit private key & rpc url, i.e: not read from env variables
# sdk = OstiumSDK(
#     network="arbitrum",
#     private_key="your_private_key_here",
#     rpc_url="https://arb1.arbitrum.io/rpc...."
# )

# Get all available pairs
pairs = await sdk.subgraph.get_pairs()

print("\nPair Information:")
print("----------------------------------------")

for pair in pairs:
    print("----------------------------------------")
    # Print all available fields in pair_details
    for key, value in pair.items():
        print(f"{key}: {value}")
    print("----------------------------------------")
```

### Opening a Trade, Reading Open Trades, Setting TP and SL, Closing a Trade

```python
# Define trade parameters
trade_params = {
    'collateral': 100,        # USDC amount
    'leverage': 10,           # Leverage multiplier
    'asset_type': 0,          # 0 for BTC, see pair_details above for other asset types 
    'direction': True,        # True for Long, False for Short
    'order_type': 'MARKET'    # 'MARKET', 'LIMIT', or 'STOP'
    #'tp': 0,                 # Take Profit price - if not specified or Zero means no TP
    #'sl': 0,                 # Stop Loss price - if not specified or Zero means no SL
}

try:
  sdk.ostium.set_slippage_percentage(1)
  print(f"Slippage percentage set to: {sdk.ostium.get_slippage_percentage()}%")

  # Get latest price for BTC
  latest_price, _, _ = await sdk.price.get_price("BTC", "USD")
  print(f"Latest price: {latest_price}")
  # Execute trade at current market price
  receipt = sdk.ostium.perform_trade(trade_params, at_price=latest_price)
  print(f"Trade successful! Transaction hash: {receipt['transactionHash'].hex()}")

  # Wait for the transaction to be confirmed
  await asyncio.sleep(10)

  # Get public address from private key
  account = Account.from_key(private_key)
  trader_public_address = account.address

  # Get the trade details
  open_trades = await sdk.subgraph.get_open_trades(trader_public_address)
  for trade_index, trade_data in enumerate(open_trades):
      print(f"Trade {trade_index + 1}: {trade_data}\n")

  if len(open_trades) == 0:
      print(
          "No open trades found. Maybe the trade failed? enough USDC and ETH in the account?")
  else:
      opened_trade = open_trades[len(open_trades) - 1]
      print(f"Opened trade: {opened_trade}\n")

      sdk.ostium.update_tp(
          opened_trade['pair']['id'], opened_trade['index'], latest_price * 1.02)
      print(f"Trade Take Profit set to 2% above the current price!\n")

      await asyncio.sleep(10)

      sdk.ostium.update_sl(
          opened_trade['pair']['id'], opened_trade['index'], latest_price * 0.99)
      print(f"Trade Stop Loss set to 1% below the current price!\n")

      await asyncio.sleep(10)

      receipt = sdk.ostium.close_trade(
          opened_trade['pair']['id'], opened_trade['index'])
      print(
          f"Closed trade! Transaction hash: {receipt['transactionHash'].hex()}\n")

except Exception as e:
  print(f"Trade failed: {str(e)}")

```


**NOTE:** Use SDK method `get_open_trade_metrics` every so often while trade is open to get the trade's metrics such as:

- Funding fee
- Roll over fee
- Unrealized Pnl and Pnl Percent
- Total Profit
- Liquidation Price 

```python
metrics = await sdk.get_open_trade_metrics(pair_id, trade_index)
print(metrics)
```

### Create a Short ETH Limit Order

This example shows how to create a short ETH limit order, 10% above the current ETHUSD price. So if price goes up 10% we order a Short ETH trade.

```python
# Get private key from environment variable
private_key = os.getenv('PRIVATE_KEY')
if not private_key:
    raise ValueError("PRIVATE_KEY not found in .env file")

rpc_url = os.getenv('RPC_URL')
if not rpc_url:
    raise ValueError("RPC_URL not found in .env file")

# Initialize SDK
config = NetworkConfig.testnet()
sdk = OstiumSDK(config, private_key, rpc_url)

# Define trade parameters
order_params = {
    'collateral': 10,         # USDC amount
    'leverage': 50,           # Leverage multiplier
    'asset_type': 1,          # 1 for ETH
    'direction': False,       # True for Long, False for Short
    'order_type': 'LIMIT'     # 'MARKET', 'LIMIT', or 'STOP'
}

try:
    # Get latest price for ETH
    latest_price, _, _ = await sdk.price.get_price("ETH", "USD")
    print(f"Latest price: {latest_price}")
    # Execute LIMIT trade order at 10% above the current price
    receipt = sdk.ostium.perform_trade(order_params, at_price=latest_price * 1.1)
    print(
        f"Order successful! Transaction hash: {receipt['transactionHash'].hex()}")

    # Wait for the order to be confirmed
    await asyncio.sleep(10)

    # Get public address from private key
    account = Account.from_key(private_key)
    trader_public_address = account.address

    # Get the order details
    open_orders = await sdk.subgraph.get_orders(trader_public_address)
    for order_index, order_data in enumerate(open_orders):
        print(f"Order {order_index + 1}: {order_data}\n")
        limit_type, _, _, _, _, _, _, pairIndex, index, _, _ = get_order_details(order_data)
        print(f"You can cancel_limit_order / update_limit_order using pair_id: {pairIndex} and index: {index}\n")
        receipt = sdk.ostium.cancel_limit_order(pairIndex, index)
        print(
        f"Limit Order cancelled! Transaction hash: {receipt['transactionHash'].hex()}")

    if len(open_orders) == 0:
        print(
            "No open order found. Maybe the order failed? enough USDC and ETH in the account?")
    else:
        opened_order = open_orders[len(open_orders) - 1]
        print(f"Opened order: {opened_order}\n")

except Exception as e:
    print(f"Order failed: {str(e)}")
```

<b>NOTE:</b> Similiarly you can create a Stop order, just use 'STOP' as the order_type and make sure at_price is set to an acceptable stop loss price.

## Example Usage Scripts

More examples can be found in the [examples](https://github.com/0xOstium/ostium_python_sdk/tree/main/examples) folder.

### Get Testnet USDC from Faucet

To get testnet USDC tokens (only available on Arbitrum Sepolia testnet):

```bash
python examples/example-faucet-request.py
```

See [example-faucet-request.py](https://github.com/0xOstium/ostium_python_sdk/blob/main/examples/example-faucet-request.py) for an example of how to use the faucet to get testnet USDC tokens.

### Read Block Number

To run the example:

```bash
python examples/example-read-block-number.py
```

See [example-read-block-number.py](https://github.com/0xOstium/ostium_python_sdk/blob/main/examples/example-read-block-number.py) for an example of how to use the SDK.

### Read Positions

To run the example:

```bash
python examples/example-read-positions.py
```

See [example-read-positions.py](https://github.com/0xOstium/ostium_python_sdk/blob/main/examples/example-read-positions.py) for an example of how to use the SDK.


### Get Feed Prices

To open a trade you need the latest feed price. 

See this example script on how to get the latest feed prices.

```bash
python examples/example-get-prices.py
```

See [example-get-prices.py](https://github.com/0xOstium/ostium_python_sdk/blob/main/examples/example-get-prices.py) for an example of how to use the SDK.



### Get Balance of an Address



See this example script on how to get the latest feed prices.

```bash
python examples/example-get-balance.py
```

See [example-get-balance.py](https://github.com/0xOstium/ostium_python_sdk/blob/main/examples/example-get-balance.py) for an example of how to use the SDK.


## Run an example from local install

```bash
 pip uninstall ostium-python-sdk  &&  pip install -e .  &&  python examples/example-pairs-details.py
```

