from gql import gql

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from decimal import Decimal


class SubgraphClient:
    def __init__(self, url: str = None, verbose=False) -> None:
        self.verbose = verbose
        transport = AIOHTTPTransport(url=url)
        self.client = Client(transport=transport,
                             fetch_schema_from_transport=True)

    def log(self, message):
        if self.verbose:
            print(message)

    async def get_pairs(self):
        self.log("Fetching available pairs")
        query = gql(
            """
          query getPairs {
              pairs(first: 1000) {
                id
                from
                to
                feed
              }
            }
      """
        )

        # Execute the query on the transport
        result = await self.client.execute_async(query)

        return result['pairs']

    async def get_pair_details(self, pair_id):
        query = gql(
            """
          query getPairDetails($pair_id: ID!){
            pair(id: $pair_id) {
              id
              from
              to                    
              longOI
              shortOI
              maxOI
              makerFeeP
              takerFeeP
              makerMaxLeverage    
              curFundingLong  
              curFundingShort
              curRollover
              totalOpenTrades
              totalOpenLimitOrders
              accRollover
              lastRolloverBlock
              rolloverFeePerBlock
              accFundingLong
              accFundingShort
              lastFundingBlock
              maxFundingFeePerBlock
              lastFundingRate              
              hillInflectionPoint
              hillPosScale
              hillNegScale
              springFactor
              sFactorUpScaleP
              sFactorDownScaleP
              lastTradePrice
              maxLeverage              
              group {
                id
                name
                minLeverage
                maxLeverage
                maxCollateralP
                longCollateral
                shortCollateral
              }
              fee {
                minLevPos                
              }
          }
          }
          """
        )
        result = await self.client.execute_async(query, variable_values={"pair_id": str(pair_id)})

        # Convert Decimal fields to float or str
        if result and 'pair' in result:
            pair = result['pair']
            for key, value in pair.items():
                if isinstance(value, Decimal):
                    pair[key] = float(value)  # or str(value) if you prefer
            return pair
        else:
            raise ValueError(f"No pair details found for pair ID: {pair_id}")

    async def get_open_trades(self, address):
        # self.log(f"Fetching open trades for address: {address}")
        query = gql(
            """
          query trades($trader: Bytes!) {
        trades(        
          where: { isOpen: true, trader: $trader }
        ) {
          tradeID
          collateral
          leverage
          highestLeverage
          openPrice
          stopLossPrice
          takeProfitPrice
          isOpen
          timestamp
          isBuy
          notional
          tradeNotional
          funding
          rollover
          trader
          index
          pair {
            id
            feed
            from
            to
            accRollover
            lastRolloverBlock
            rolloverFeePerBlock
            accFundingLong
            spreadP
            accFundingShort
            longOI
            shortOI
            maxOI
            hillInflectionPoint
            hillPosScale
            hillNegScale
            springFactor
            sFactorUpScaleP
            sFactorDownScaleP
            lastFundingBlock
            maxFundingFeePerBlock
            lastFundingRate
          }
        }
      }
          """
        )
        result = await self.client.execute_async(query, variable_values={"trader": address})
        return result['trades']

    async def get_orders(self, trader):
        query = gql(
            """
          query orders($trader: Bytes!) {
            limits(
              where: { trader: $trader, isActive: true }
              orderBy: initiatedAt
              orderDirection: asc
            ) {
              collateral
              leverage
              isBuy
              isActive
              id
              openPrice
              takeProfitPrice
              stopLossPrice
              trader
              initiatedAt
              limitType
              pair {
                id
                feed
                from
                to
                accRollover
                lastRolloverBlock
                rolloverFeePerBlock
                accFundingLong
                spreadP
                accFundingShort
                longOI
                shortOI
                lastFundingBlock
                maxFundingFeePerBlock
                lastFundingRate
              }
            }
          }
          """
        )
        result = await self.client.execute_async(query, variable_values={"trader": trader})

        return result['limits']

    async def get_recent_history(self, trader, last_n_orders=10):
        query = gql(
            """
        query ListOrdersHistory($trader: Bytes, $last_n_orders: Int) {
          orders(
            where: { trader: $trader, isPending: false}
            first: $last_n_orders
            orderBy: executedAt
            orderDirection: desc
          ) {
            id
            isBuy
            trader
            notional
            tradeNotional
            collateral
            leverage
            orderType
            orderAction
            price
            initiatedAt
            executedAt
            executedTx
            isCancelled
            cancelReason
            profitPercent
            totalProfitPercent
            isPending
            amountSentToTrader
            rolloverFee
            fundingFee
            pair {
              id
              from
              to
              feed
              longOI
              shortOI
              group {
                  name
              }
            }
          }
        }
        """
        )
        result = await self.client.execute_async(query, variable_values={"trader": trader, "last_n_orders": last_n_orders})

        return list(reversed(result['orders']))  # Reverse the final list

    async def get_order_by_id(self, order_id):
        """
        Get an order by its ID
        """
        query = gql(
            """
            query GetOrder($order_id: ID!) {
              orders(where: {id: $order_id}) {
                id
                trader
                pair {
                  id
                  from
                  to
                  feed
                }
                tradeID
                limitID
                orderType
                orderAction
                price
                priceAfterImpact
                priceImpactP
                collateral
                notional
                tradeNotional
                profitPercent
                totalProfitPercent
                amountSentToTrader
                isBuy
                initiatedAt
                executedAt
                initiatedTx
                executedTx
                initiatedBlock
                executedBlock
                leverage
                isPending
                isCancelled
                cancelReason
                devFee
                vaultFee
                oracleFee
                liquidationFee
                fundingFee
                rolloverFee
                closePercent
              }
            }
            """
        )
        
        result = await self.client.execute_async(query, variable_values={"order_id": str(order_id)})
        
        if result and 'orders' in result and len(result['orders']) > 0:
            return result['orders'][0]
        return None

    async def get_trade_by_id(self, trade_id):
        """
        Get a trade by its ID
        """
        query = gql(
            """
            query GetTrade($trade_id: ID!) {
              trades(where: {id: $trade_id}) {
                id
                trader
                pair {
                  id
                  from
                  to
                  feed
                }
                index
                tradeID
                tradeType
                openPrice
                closePrice
                takeProfitPrice
                stopLossPrice
                collateral
                notional
                tradeNotional
                highestLeverage
                leverage
                isBuy
                isOpen
                closeInitiated
                funding
                rollover
                timestamp
              }
            }
            """
        )
        
        result = await self.client.execute_async(query, variable_values={"trade_id": str(trade_id)})
        
        if result and 'trades' in result and len(result['trades']) > 0:
            return result['trades'][0]
        return None