callbacks_abi = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "InvalidInitialization",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "IsDone",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "IsPaused",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "a",
                "type": "address"
            }
        ],
        "name": "NotGov",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "NotInitializing",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "a",
                "type": "address"
            }
        ],
        "name": "NotManager",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "a",
                "type": "address"
            }
        ],
        "name": "NotPriceUpKeep",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "a",
                "type": "address"
            }
        ],
        "name": "NotTrading",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "uint8",
                "name": "bits",
                "type": "uint8"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "SafeCastOverflowedUintDowncast",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "SafeCastOverflowedUintToInt",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "token",
                "type": "address"
            }
        ],
        "name": "SafeERC20FailedOperation",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "WrongParams",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "pairIndex",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "enum IOstiumTradingStorage.LimitOrder",
                "name": "orderType",
                "type": "uint8"
            },
            {
                "indexed": False,
                "internalType": "enum IOstiumTradingCallbacks.CancelReason",
                "name": "cancelReason",
                "type": "uint8"
            }
        ],
        "name": "AutomationCloseOrderCanceled",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "pairIndex",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "enum IOstiumTradingCallbacks.CancelReason",
                "name": "cancelReason",
                "type": "uint8"
            }
        ],
        "name": "AutomationOpenOrderCanceled",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "builder",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "BuilderFeeCharged",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "closeFee",
                "type": "uint256"
            }
        ],
        "name": "CloseFeeCharged",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint32",
                "name": "decayWindow",
                "type": "uint32"
            },
            {
                "indexed": False,
                "internalType": "uint32",
                "name": "startingP",
                "type": "uint32"
            }
        ],
        "name": "CloseFeeParamsUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "DevFeeCharged",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "bool",
                "name": "done",
                "type": "bool"
            }
        ],
        "name": "Done",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "rolloverFees",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "fundingFees",
                "type": "int256"
            }
        ],
        "name": "FeesCharged",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "rolloverFees",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "fundingFees",
                "type": "int256"
            }
        ],
        "name": "FeesChargedV2",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint64",
                "name": "version",
                "type": "uint64"
            }
        ],
        "name": "Initialized",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "enum IOstiumTradingStorage.LimitOrder",
                "name": "orderType",
                "type": "uint8"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "price",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "priceImpactP",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "percentProfit",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "usdcSentToTrader",
                "type": "uint256"
            }
        ],
        "name": "LimitCloseExecuted",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "limitIndex",
                "type": "uint256"
            },
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "collateral",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint192",
                        "name": "openPrice",
                        "type": "uint192"
                    },
                    {
                        "internalType": "uint192",
                        "name": "tp",
                        "type": "uint192"
                    },
                    {
                        "internalType": "uint192",
                        "name": "sl",
                        "type": "uint192"
                    },
                    {
                        "internalType": "address",
                        "name": "trader",
                        "type": "address"
                    },
                    {
                        "internalType": "uint32",
                        "name": "leverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "pairIndex",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint8",
                        "name": "index",
                        "type": "uint8"
                    },
                    {
                        "internalType": "bool",
                        "name": "buy",
                        "type": "bool"
                    },
                    {
                        "internalType": "bool",
                        "name": "isDayTrade",
                        "type": "bool"
                    }
                ],
                "indexed": False,
                "internalType": "struct IOstiumTradingStorage.Trade",
                "name": "t",
                "type": "tuple"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "priceImpactP",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "tradeNotional",
                "type": "uint256"
            }
        ],
        "name": "LimitOpenExecuted",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "pairIndex",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "index",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "enum IOstiumTradingCallbacks.CancelReason",
                "name": "cancelReason",
                "type": "uint8"
            }
        ],
        "name": "MarketCloseCanceled",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "price",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "priceImpactP",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "percentProfit",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "usdcSentToTrader",
                "type": "uint256"
            }
        ],
        "name": "MarketCloseExecuted",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "price",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "priceImpactP",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "percentProfit",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "usdcSentToTrader",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "percentageClosed",
                "type": "uint256"
            }
        ],
        "name": "MarketCloseExecutedV2",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "pairIndex",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "enum IOstiumTradingCallbacks.CancelReason",
                "name": "cancelReason",
                "type": "uint8"
            }
        ],
        "name": "MarketOpenCanceled",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "collateral",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint192",
                        "name": "openPrice",
                        "type": "uint192"
                    },
                    {
                        "internalType": "uint192",
                        "name": "tp",
                        "type": "uint192"
                    },
                    {
                        "internalType": "uint192",
                        "name": "sl",
                        "type": "uint192"
                    },
                    {
                        "internalType": "address",
                        "name": "trader",
                        "type": "address"
                    },
                    {
                        "internalType": "uint32",
                        "name": "leverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "pairIndex",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint8",
                        "name": "index",
                        "type": "uint8"
                    },
                    {
                        "internalType": "bool",
                        "name": "buy",
                        "type": "bool"
                    },
                    {
                        "internalType": "bool",
                        "name": "isDayTrade",
                        "type": "bool"
                    }
                ],
                "indexed": False,
                "internalType": "struct IOstiumTradingStorage.Trade",
                "name": "t",
                "type": "tuple"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "priceImpactP",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "tradeNotional",
                "type": "uint256"
            }
        ],
        "name": "MarketOpenExecuted",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "MaxSlPUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "OracleFeeCharged",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "OracleFeeRefunded",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "bool",
                "name": "paused",
                "type": "bool"
            }
        ],
        "name": "Paused",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "removeAmount",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            },
            {
                "indexed": False,
                "internalType": "uint192",
                "name": "tp",
                "type": "uint192"
            },
            {
                "indexed": False,
                "internalType": "uint192",
                "name": "sl",
                "type": "uint192"
            }
        ],
        "name": "RemoveCollateralExecuted",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "removeAmount",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "enum IOstiumTradingCallbacks.CancelReason",
                "name": "reason",
                "type": "uint8"
            }
        ],
        "name": "RemoveCollateralRejected",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "TradeSizeRefUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "orderId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "VaultLiqFeeCharged",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "VaultOpeningFeeCharged",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "closeFeeDecayWindow",
        "outputs": [
            {
                "internalType": "uint32",
                "name": "",
                "type": "uint32"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "closeFeeStartingP",
        "outputs": [
            {
                "internalType": "uint32",
                "name": "",
                "type": "uint32"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "orderId",
                        "type": "uint256"
                    },
                    {
                        "internalType": "int192",
                        "name": "price",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "bid",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "ask",
                        "type": "int192"
                    },
                    {
                        "internalType": "bool",
                        "name": "isDayTradingClosed",
                        "type": "bool"
                    }
                ],
                "internalType": "struct IOstiumPriceUpKeep.PriceUpKeepAnswer",
                "name": "a",
                "type": "tuple"
            }
        ],
        "name": "closeTradeMarketCallback",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "done",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "orderId",
                        "type": "uint256"
                    },
                    {
                        "internalType": "int192",
                        "name": "price",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "bid",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "ask",
                        "type": "int192"
                    },
                    {
                        "internalType": "bool",
                        "name": "isDayTradingClosed",
                        "type": "bool"
                    }
                ],
                "internalType": "struct IOstiumPriceUpKeep.PriceUpKeepAnswer",
                "name": "a",
                "type": "tuple"
            }
        ],
        "name": "executeAutomationCloseOrderCallback",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "orderId",
                        "type": "uint256"
                    },
                    {
                        "internalType": "int192",
                        "name": "price",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "bid",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "ask",
                        "type": "int192"
                    },
                    {
                        "internalType": "bool",
                        "name": "isDayTradingClosed",
                        "type": "bool"
                    }
                ],
                "internalType": "struct IOstiumPriceUpKeep.PriceUpKeepAnswer",
                "name": "a",
                "type": "tuple"
            }
        ],
        "name": "executeAutomationOpenOrderCallback",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "orderId",
                        "type": "uint256"
                    },
                    {
                        "internalType": "int192",
                        "name": "price",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "bid",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "ask",
                        "type": "int192"
                    },
                    {
                        "internalType": "bool",
                        "name": "isDayTradingClosed",
                        "type": "bool"
                    }
                ],
                "internalType": "struct IOstiumPriceUpKeep.PriceUpKeepAnswer",
                "name": "a",
                "type": "tuple"
            }
        ],
        "name": "handleRemoveCollateral",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "contract IOstiumRegistry",
                "name": "_registry",
                "type": "address"
            }
        ],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "isDone",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "isPaused",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "maxSl_P",
        "outputs": [
            {
                "internalType": "uint8",
                "name": "",
                "type": "uint8"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "orderId",
                        "type": "uint256"
                    },
                    {
                        "internalType": "int192",
                        "name": "price",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "bid",
                        "type": "int192"
                    },
                    {
                        "internalType": "int192",
                        "name": "ask",
                        "type": "int192"
                    },
                    {
                        "internalType": "bool",
                        "name": "isDayTradingClosed",
                        "type": "bool"
                    }
                ],
                "internalType": "struct IOstiumPriceUpKeep.PriceUpKeepAnswer",
                "name": "a",
                "type": "tuple"
            }
        ],
        "name": "openTradeMarketCallback",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "pause",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "registry",
        "outputs": [
            {
                "internalType": "contract IOstiumRegistry",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint32",
                "name": "_decayWindow",
                "type": "uint32"
            },
            {
                "internalType": "uint32",
                "name": "_startingP",
                "type": "uint32"
            }
        ],
        "name": "setCloseFeeParams",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_maxSl_P",
                "type": "uint256"
            }
        ],
        "name": "setMaxSl_P",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "setVaultMaxAllowance",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_oldVault",
                "type": "address"
            }
        ],
        "name": "unsetVaultMaxAllowance",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
