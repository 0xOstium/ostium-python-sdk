pairs_info_abi = [
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
        "inputs": [
            {
                "internalType": "address",
                "name": "a",
                "type": "address"
            }
        ],
        "name": "NotCallbacks",
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
                "internalType": "uint8",
                "name": "bits",
                "type": "uint8"
            },
            {
                "internalType": "int256",
                "name": "value",
                "type": "int256"
            }
        ],
        "name": "SafeCastOverflowedIntDowncast",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "int256",
                "name": "value",
                "type": "int256"
            }
        ],
        "name": "SafeCastOverflowedIntToUint",
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
        "inputs": [],
        "name": "WrongParams",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "valueLong",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "valueShort",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "int64",
                "name": "lastFundingRate",
                "type": "int64"
            },
            {
                "indexed": False,
                "internalType": "int64",
                "name": "velocity",
                "type": "int64"
            }
        ],
        "name": "AccFundingFeesStored",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "valueLong",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "valueShort",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "lastOiDelta",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "int64",
                "name": "lastFundingRate",
                "type": "int64"
            }
        ],
        "name": "AccFundingFeesStoredV2",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "AccRolloverFeesStored",
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
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "FundingFeeSlopeUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "hillInflectionPoint",
                "type": "int256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "hillPosScale",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "hillNegScale",
                "type": "uint256"
            }
        ],
        "name": "HillParamsUpdated",
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
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "int64",
                "name": "value",
                "type": "int64"
            }
        ],
        "name": "LastVelocityUpdated",
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
        "name": "LiqMarginThresholdPUpdated",
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
        "name": "LiqThresholdPUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "value",
                "type": "address"
            }
        ],
        "name": "ManagerUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "MaxFundingFeePerBlockUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "MaxFundingFeeVelocityUpdated",
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
        "name": "MaxNegativePnlOnOpenPUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "MaxRolloverFeePerBlockUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "MaxRolloverFeeSlopeUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "MaxRolloverVolatilityUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "components": [
                    {
                        "internalType": "int256",
                        "name": "accPerOiLong",
                        "type": "int256"
                    },
                    {
                        "internalType": "int256",
                        "name": "accPerOiShort",
                        "type": "int256"
                    },
                    {
                        "internalType": "int64",
                        "name": "lastFundingRate",
                        "type": "int64"
                    },
                    {
                        "internalType": "int64",
                        "name": "lastVelocity",
                        "type": "int64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "maxFundingFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "maxFundingFeeVelocity",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "lastUpdateBlock",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "fundingFeeSlope",
                        "type": "uint16"
                    }
                ],
                "indexed": False,
                "internalType": "struct IOstiumPairInfos.PairFundingFees",
                "name": "value",
                "type": "tuple"
            }
        ],
        "name": "PairFundingFeesUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "components": [
                    {
                        "internalType": "int256",
                        "name": "accPerOiLong",
                        "type": "int256"
                    },
                    {
                        "internalType": "int256",
                        "name": "accPerOiShort",
                        "type": "int256"
                    },
                    {
                        "internalType": "int64",
                        "name": "lastFundingRate",
                        "type": "int64"
                    },
                    {
                        "internalType": "int64",
                        "name": "hillInflectionPoint",
                        "type": "int64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "maxFundingFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "springFactor",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "lastUpdateBlock",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "hillPosScale",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "hillNegScale",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "sFactorUpScaleP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "sFactorDownScaleP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "int256",
                        "name": "lastOiDelta",
                        "type": "int256"
                    }
                ],
                "indexed": False,
                "internalType": "struct IOstiumPairInfos.PairFundingFeesV2",
                "name": "value",
                "type": "tuple"
            }
        ],
        "name": "PairFundingFeesUpdatedV2",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "components": [
                    {
                        "internalType": "uint32",
                        "name": "makerFeeP",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "takerFeeP",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "usageFeeP",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "utilizationThresholdP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "makerMaxLeverage",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint8",
                        "name": "vaultFeePercent",
                        "type": "uint8"
                    }
                ],
                "indexed": False,
                "internalType": "struct IOstiumPairInfos.PairOpeningFees",
                "name": "value",
                "type": "tuple"
            }
        ],
        "name": "PairOpeningFeesUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "accPerOi",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint64",
                        "name": "rolloverFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "maxRolloverFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxRolloverVolatility",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "lastUpdateBlock",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "rolloverFeeSlope",
                        "type": "uint16"
                    }
                ],
                "indexed": False,
                "internalType": "struct IOstiumPairInfos.PairRolloverFees",
                "name": "value",
                "type": "tuple"
            }
        ],
        "name": "PairRolloverFeesUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "volatility",
                "type": "uint256"
            }
        ],
        "name": "RolloverFeePerBlockUpdated",
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
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint8",
                "name": "index",
                "type": "uint8"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "rollover",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "int256",
                "name": "funding",
                "type": "int256"
            }
        ],
        "name": "TradeInitialAccFeesStored",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "uint8",
                "name": "value",
                "type": "uint8"
            }
        ],
        "name": "VaultFeePercentUpdated",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getAccFundingFeesLong",
        "outputs": [
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getAccFundingFeesShort",
        "outputs": [
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getAccFundingFeesUpdateBlock",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getAccRolloverFees",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getAccRolloverFeesUpdateBlock",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getFrSpringFactor",
        "outputs": [
            {
                "internalType": "uint64",
                "name": "",
                "type": "uint64"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getHillFunctionParams",
        "outputs": [
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            },
            {
                "internalType": "uint16",
                "name": "",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "",
                "type": "uint16"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "int256",
                "name": "leveragedPositionSize",
                "type": "int256"
            },
            {
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            },
            {
                "internalType": "int256",
                "name": "oiDelta",
                "type": "int256"
            }
        ],
        "name": "getOpeningFee",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "devFee",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "vaultFee",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getPendingAccFundingFees",
        "outputs": [
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            },
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            },
            {
                "internalType": "int64",
                "name": "",
                "type": "int64"
            },
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getPendingAccRolloverFees",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "getRolloverFeePerBlock",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "trader",
                "type": "address"
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
                "name": "long",
                "type": "bool"
            },
            {
                "internalType": "uint256",
                "name": "collateral",
                "type": "uint256"
            },
            {
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            }
        ],
        "name": "getTradeFundingFee",
        "outputs": [
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            },
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "int256",
                "name": "accFundingFeesPerOi",
                "type": "int256"
            },
            {
                "internalType": "int256",
                "name": "endAccFundingFeesPerOi",
                "type": "int256"
            },
            {
                "internalType": "uint256",
                "name": "collateral",
                "type": "uint256"
            },
            {
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            }
        ],
        "name": "getTradeFundingFeePure",
        "outputs": [
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            }
        ],
        "stateMutability": "pure",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "trader",
                "type": "address"
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
            }
        ],
        "name": "getTradeInitialAccFundingFeesPerOi",
        "outputs": [
            {
                "internalType": "int256",
                "name": "",
                "type": "int256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "trader",
                "type": "address"
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
            }
        ],
        "name": "getTradeInitialAccRolloverFeesPerCollateral",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "collateral",
                "type": "uint256"
            },
            {
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            },
            {
                "internalType": "uint32",
                "name": "maxLeverage",
                "type": "uint32"
            }
        ],
        "name": "getTradeLiquidationMargin",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "trader",
                "type": "address"
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
                "internalType": "uint256",
                "name": "openPrice",
                "type": "uint256"
            },
            {
                "internalType": "bool",
                "name": "long",
                "type": "bool"
            },
            {
                "internalType": "uint256",
                "name": "collateral",
                "type": "uint256"
            },
            {
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            },
            {
                "internalType": "uint32",
                "name": "maxLeverage",
                "type": "uint32"
            }
        ],
        "name": "getTradeLiquidationPrice",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "openPrice",
                "type": "uint256"
            },
            {
                "internalType": "bool",
                "name": "long",
                "type": "bool"
            },
            {
                "internalType": "uint256",
                "name": "collateral",
                "type": "uint256"
            },
            {
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            },
            {
                "internalType": "uint256",
                "name": "rolloverFee",
                "type": "uint256"
            },
            {
                "internalType": "int256",
                "name": "fundingFee",
                "type": "int256"
            },
            {
                "internalType": "uint32",
                "name": "maxLeverage",
                "type": "uint32"
            }
        ],
        "name": "getTradeLiquidationPricePure",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "trader",
                "type": "address"
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
                "internalType": "uint256",
                "name": "collateral",
                "type": "uint256"
            },
            {
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            }
        ],
        "name": "getTradeRolloverFee",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "accRolloverFeesPerCollateral",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "endAccRolloverFeesPerCollateral",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "collateral",
                "type": "uint256"
            },
            {
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            }
        ],
        "name": "getTradeRolloverFeePure",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "pure",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "trader",
                "type": "address"
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
                "name": "long",
                "type": "bool"
            },
            {
                "internalType": "uint256",
                "name": "collateral",
                "type": "uint256"
            },
            {
                "internalType": "uint32",
                "name": "leverage",
                "type": "uint32"
            },
            {
                "internalType": "int256",
                "name": "percentProfit",
                "type": "int256"
            },
            {
                "internalType": "uint32",
                "name": "maxLeverage",
                "type": "uint32"
            }
        ],
        "name": "getTradeValue",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "tradeValue",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "liqMarginValue",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "r",
                "type": "uint256"
            },
            {
                "internalType": "int256",
                "name": "f",
                "type": "int256"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "collateral",
                "type": "uint256"
            },
            {
                "internalType": "int256",
                "name": "percentProfit",
                "type": "int256"
            },
            {
                "internalType": "uint256",
                "name": "rolloverFee",
                "type": "uint256"
            },
            {
                "internalType": "int256",
                "name": "fundingFee",
                "type": "int256"
            },
            {
                "internalType": "uint256",
                "name": "liqMarginValue",
                "type": "uint256"
            }
        ],
        "name": "getTradeValuePure",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "pure",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "contract IOstiumRegistry",
                "name": "_registry",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "_manager",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "_liqMarginThresholdP",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_maxNegativePnlOnOpenP",
                "type": "uint256"
            }
        ],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "int256",
                        "name": "accPerOiLong",
                        "type": "int256"
                    },
                    {
                        "internalType": "int256",
                        "name": "accPerOiShort",
                        "type": "int256"
                    },
                    {
                        "internalType": "int64",
                        "name": "lastFundingRate",
                        "type": "int64"
                    },
                    {
                        "internalType": "int64",
                        "name": "hillInflectionPoint",
                        "type": "int64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "maxFundingFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "springFactor",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "lastUpdateBlock",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "hillPosScale",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "hillNegScale",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "sFactorUpScaleP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "sFactorDownScaleP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "int256",
                        "name": "lastOiDelta",
                        "type": "int256"
                    }
                ],
                "internalType": "struct IOstiumPairInfos.PairFundingFeesV2[]",
                "name": "value",
                "type": "tuple[]"
            }
        ],
        "name": "initializeV2",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_liqMarginThresholdP",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_maxNegativePnlOnOpenP",
                "type": "uint256"
            }
        ],
        "name": "initializeV3",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "liqMarginThresholdP",
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
        "inputs": [],
        "name": "manager",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "maxNegativePnlOnOpenP",
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
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairFundingFees",
        "outputs": [
            {
                "internalType": "int256",
                "name": "accPerOiLong",
                "type": "int256"
            },
            {
                "internalType": "int256",
                "name": "accPerOiShort",
                "type": "int256"
            },
            {
                "internalType": "int64",
                "name": "lastFundingRate",
                "type": "int64"
            },
            {
                "internalType": "int64",
                "name": "hillInflectionPoint",
                "type": "int64"
            },
            {
                "internalType": "uint64",
                "name": "maxFundingFeePerBlock",
                "type": "uint64"
            },
            {
                "internalType": "uint64",
                "name": "springFactor",
                "type": "uint64"
            },
            {
                "internalType": "uint32",
                "name": "lastUpdateBlock",
                "type": "uint32"
            },
            {
                "internalType": "uint16",
                "name": "hillPosScale",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "hillNegScale",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "sFactorUpScaleP",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "sFactorDownScaleP",
                "type": "uint16"
            },
            {
                "internalType": "int256",
                "name": "lastOiDelta",
                "type": "int256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairOpeningFees",
        "outputs": [
            {
                "internalType": "uint32",
                "name": "makerFeeP",
                "type": "uint32"
            },
            {
                "internalType": "uint32",
                "name": "takerFeeP",
                "type": "uint32"
            },
            {
                "internalType": "uint32",
                "name": "usageFeeP",
                "type": "uint32"
            },
            {
                "internalType": "uint16",
                "name": "utilizationThresholdP",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "makerMaxLeverage",
                "type": "uint16"
            },
            {
                "internalType": "uint8",
                "name": "vaultFeePercent",
                "type": "uint8"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairRolloverFees",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "accPerOi",
                "type": "uint256"
            },
            {
                "internalType": "uint64",
                "name": "rolloverFeePerBlock",
                "type": "uint64"
            },
            {
                "internalType": "uint64",
                "name": "maxRolloverFeePerBlock",
                "type": "uint64"
            },
            {
                "internalType": "uint32",
                "name": "maxRolloverVolatility",
                "type": "uint32"
            },
            {
                "internalType": "uint32",
                "name": "lastUpdateBlock",
                "type": "uint32"
            },
            {
                "internalType": "uint16",
                "name": "rolloverFeeSlope",
                "type": "uint16"
            }
        ],
        "stateMutability": "view",
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
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "int256",
                "name": "hillInflectionPoint",
                "type": "int256"
            },
            {
                "internalType": "uint256",
                "name": "hillPosScale",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "hillNegScale",
                "type": "uint256"
            }
        ],
        "name": "setHillFunctionParams",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "internalType": "int256[]",
                "name": "hillInflectionPoints",
                "type": "int256[]"
            },
            {
                "internalType": "uint256[]",
                "name": "hillPosScales",
                "type": "uint256[]"
            },
            {
                "internalType": "uint256[]",
                "name": "hillNegScales",
                "type": "uint256[]"
            }
        ],
        "name": "setHillFunctionParamsArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "setLiqMarginThresholdP",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_manager",
                "type": "address"
            }
        ],
        "name": "setManager",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "setMaxFundingFeePerBlock",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "internalType": "uint256[]",
                "name": "values",
                "type": "uint256[]"
            }
        ],
        "name": "setMaxFundingFeePerBlockArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "setMaxNegativePnlOnOpenP",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "setMaxRolloverFeePerBlock",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "internalType": "uint256[]",
                "name": "values",
                "type": "uint256[]"
            }
        ],
        "name": "setMaxRolloverFeePerBlockArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "setMaxRolloverVolatility",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "internalType": "uint256[]",
                "name": "values",
                "type": "uint256[]"
            }
        ],
        "name": "setMaxRolloverVolatilityArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "components": [
                    {
                        "internalType": "int256",
                        "name": "accPerOiLong",
                        "type": "int256"
                    },
                    {
                        "internalType": "int256",
                        "name": "accPerOiShort",
                        "type": "int256"
                    },
                    {
                        "internalType": "int64",
                        "name": "lastFundingRate",
                        "type": "int64"
                    },
                    {
                        "internalType": "int64",
                        "name": "hillInflectionPoint",
                        "type": "int64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "maxFundingFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "springFactor",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "lastUpdateBlock",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "hillPosScale",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "hillNegScale",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "sFactorUpScaleP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "sFactorDownScaleP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "int256",
                        "name": "lastOiDelta",
                        "type": "int256"
                    }
                ],
                "internalType": "struct IOstiumPairInfos.PairFundingFeesV2",
                "name": "value",
                "type": "tuple"
            }
        ],
        "name": "setPairFundingFees",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "components": [
                    {
                        "internalType": "int256",
                        "name": "accPerOiLong",
                        "type": "int256"
                    },
                    {
                        "internalType": "int256",
                        "name": "accPerOiShort",
                        "type": "int256"
                    },
                    {
                        "internalType": "int64",
                        "name": "lastFundingRate",
                        "type": "int64"
                    },
                    {
                        "internalType": "int64",
                        "name": "hillInflectionPoint",
                        "type": "int64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "maxFundingFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "springFactor",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "lastUpdateBlock",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "hillPosScale",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "hillNegScale",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "sFactorUpScaleP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "sFactorDownScaleP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "int256",
                        "name": "lastOiDelta",
                        "type": "int256"
                    }
                ],
                "internalType": "struct IOstiumPairInfos.PairFundingFeesV2[]",
                "name": "values",
                "type": "tuple[]"
            }
        ],
        "name": "setPairFundingFeesArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "components": [
                    {
                        "internalType": "uint32",
                        "name": "makerFeeP",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "takerFeeP",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "usageFeeP",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "utilizationThresholdP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "makerMaxLeverage",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint8",
                        "name": "vaultFeePercent",
                        "type": "uint8"
                    }
                ],
                "internalType": "struct IOstiumPairInfos.PairOpeningFees",
                "name": "value",
                "type": "tuple"
            }
        ],
        "name": "setPairOpeningFees",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "components": [
                    {
                        "internalType": "uint32",
                        "name": "makerFeeP",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "takerFeeP",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "usageFeeP",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "utilizationThresholdP",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "makerMaxLeverage",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint8",
                        "name": "vaultFeePercent",
                        "type": "uint8"
                    }
                ],
                "internalType": "struct IOstiumPairInfos.PairOpeningFees[]",
                "name": "values",
                "type": "tuple[]"
            }
        ],
        "name": "setPairOpeningFeesArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint8",
                "name": "value",
                "type": "uint8"
            }
        ],
        "name": "setPairOpeningVaultFeePercent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "internalType": "uint8[]",
                "name": "values",
                "type": "uint8[]"
            }
        ],
        "name": "setPairOpeningVaultFeePercentArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "accPerOi",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint64",
                        "name": "rolloverFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "maxRolloverFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxRolloverVolatility",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "lastUpdateBlock",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "rolloverFeeSlope",
                        "type": "uint16"
                    }
                ],
                "internalType": "struct IOstiumPairInfos.PairRolloverFees",
                "name": "value",
                "type": "tuple"
            }
        ],
        "name": "setPairRolloverFees",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "accPerOi",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint64",
                        "name": "rolloverFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "maxRolloverFeePerBlock",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxRolloverVolatility",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "lastUpdateBlock",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "rolloverFeeSlope",
                        "type": "uint16"
                    }
                ],
                "internalType": "struct IOstiumPairInfos.PairRolloverFees[]",
                "name": "values",
                "type": "tuple[]"
            }
        ],
        "name": "setPairRolloverFeesArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint256",
                "name": "volatility",
                "type": "uint256"
            }
        ],
        "name": "setRolloverFeePerBlock",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "internalType": "uint256[]",
                "name": "values",
                "type": "uint256[]"
            }
        ],
        "name": "setRolloverFeePerBlockArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "setRolloverFeeSlope",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "internalType": "uint256[]",
                "name": "values",
                "type": "uint256[]"
            }
        ],
        "name": "setRolloverFeeSlopeArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "tradeId",
                "type": "uint256"
            },
            {
                "internalType": "address",
                "name": "trader",
                "type": "address"
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
                "name": "long",
                "type": "bool"
            }
        ],
        "name": "storeTradeInitialAccFees",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "trader",
                "type": "address"
            },
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint8",
                "name": "tradeIndex",
                "type": "uint8"
            }
        ],
        "name": "tradeInitialAccFees",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "rollover",
                "type": "uint256"
            },
            {
                "internalType": "int256",
                "name": "funding",
                "type": "int256"
            },
            {
                "internalType": "bool",
                "name": "openedAfterUpdate",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
