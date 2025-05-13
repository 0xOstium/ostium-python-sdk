pairs_storage_abi = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "index",
                "type": "uint256"
            }
        ],
        "name": "FeeNotListed",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "index",
                "type": "uint256"
            }
        ],
        "name": "GroupNotListed",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "InvalidInitialization",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "MaxReached",
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
        "name": "NotAuthorized",
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
                "internalType": "bytes32",
                "name": "from",
                "type": "bytes32"
            },
            {
                "internalType": "bytes32",
                "name": "to",
                "type": "bytes32"
            }
        ],
        "name": "PairAlreadyListed",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "PairNotEmpty",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "index",
                "type": "uint256"
            }
        ],
        "name": "PairNotListed",
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
        "inputs": [],
        "name": "WrongParams",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint8",
                "name": "index",
                "type": "uint8"
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "name",
                "type": "bytes32"
            }
        ],
        "name": "FeeAdded",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint8",
                "name": "index",
                "type": "uint8"
            }
        ],
        "name": "FeeUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint8",
                "name": "index",
                "type": "uint8"
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "name",
                "type": "bytes32"
            }
        ],
        "name": "GroupAdded",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint8",
                "name": "index",
                "type": "uint8"
            }
        ],
        "name": "GroupUpdated",
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
                "indexed": False,
                "internalType": "uint16",
                "name": "index",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "from",
                "type": "bytes32"
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "to",
                "type": "bytes32"
            }
        ],
        "name": "PairAdded",
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
                "internalType": "bytes32",
                "name": "feed",
                "type": "bytes32"
            }
        ],
        "name": "PairFeedUpdated",
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
                "internalType": "uint32",
                "name": "maxLeverage",
                "type": "uint32"
            }
        ],
        "name": "PairMaxLeverageUpdated",
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
                "internalType": "uint32",
                "name": "overnightMaxLeverage",
                "type": "uint32"
            }
        ],
        "name": "PairOvernightMaxLeverageUpdated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint16",
                "name": "index",
                "type": "uint16"
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "from",
                "type": "bytes32"
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "to",
                "type": "bytes32"
            }
        ],
        "name": "PairRemoved",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "index",
                "type": "uint16"
            }
        ],
        "name": "PairUpdated",
        "type": "event"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "name",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint64",
                        "name": "minLevPos",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "oracleFee",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint16",
                        "name": "liqFeeP",
                        "type": "uint16"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Fee",
                "name": "_fee",
                "type": "tuple"
            }
        ],
        "name": "addFee",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "name",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "minLeverage",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "maxCollateralP",
                        "type": "uint16"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Group",
                "name": "_group",
                "type": "tuple"
            }
        ],
        "name": "addGroup",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "from",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "to",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "feed",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint64",
                        "name": "tradeSizeRef",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "overnightMaxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint8",
                        "name": "groupIndex",
                        "type": "uint8"
                    },
                    {
                        "internalType": "uint8",
                        "name": "feeIndex",
                        "type": "uint8"
                    },
                    {
                        "internalType": "string",
                        "name": "oracle",
                        "type": "string"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Pair",
                "name": "_pair",
                "type": "tuple"
            }
        ],
        "name": "addPair",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "from",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "to",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "feed",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint64",
                        "name": "tradeSizeRef",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "overnightMaxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint8",
                        "name": "groupIndex",
                        "type": "uint8"
                    },
                    {
                        "internalType": "uint8",
                        "name": "feeIndex",
                        "type": "uint8"
                    },
                    {
                        "internalType": "string",
                        "name": "oracle",
                        "type": "string"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Pair[]",
                "name": "_pairs",
                "type": "tuple[]"
            }
        ],
        "name": "addPairs",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint8",
                "name": "feeIndex",
                "type": "uint8"
            }
        ],
        "name": "fees",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "name",
                "type": "bytes32"
            },
            {
                "internalType": "uint64",
                "name": "minLevPos",
                "type": "uint64"
            },
            {
                "internalType": "uint64",
                "name": "oracleFee",
                "type": "uint64"
            },
            {
                "internalType": "uint16",
                "name": "liqFeeP",
                "type": "uint16"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "feesCount",
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
        "name": "getAllPairsMaxLeverage",
        "outputs": [
            {
                "internalType": "uint32[]",
                "name": "",
                "type": "uint32[]"
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
        "name": "getFeedInfo",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "",
                "type": "bytes32"
            },
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
                "internalType": "uint256",
                "name": "startId",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "finalId",
                "type": "uint256"
            }
        ],
        "name": "getPairsMaxLeverage",
        "outputs": [
            {
                "internalType": "uint32[]",
                "name": "",
                "type": "uint32[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "_pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "bool",
                "name": "_long",
                "type": "bool"
            }
        ],
        "name": "groupCollateral",
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
                "name": "_pairIndex",
                "type": "uint16"
            }
        ],
        "name": "groupMaxCollateral",
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
                "internalType": "uint8",
                "name": "groupIndex",
                "type": "uint8"
            }
        ],
        "name": "groups",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "name",
                "type": "bytes32"
            },
            {
                "internalType": "uint32",
                "name": "maxLeverage",
                "type": "uint32"
            },
            {
                "internalType": "uint16",
                "name": "minLeverage",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "maxCollateralP",
                "type": "uint16"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint8",
                "name": "groupIndex",
                "type": "uint8"
            },
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "name": "groupsCollaterals",
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
        "inputs": [],
        "name": "groupsCount",
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
        "inputs": [
            {
                "internalType": "uint16[]",
                "name": "indices",
                "type": "uint16[]"
            },
            {
                "internalType": "uint32[]",
                "name": "overnightMaxLeverages",
                "type": "uint32[]"
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
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "isPairIndexListed",
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
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "fromPair",
                "type": "bytes32"
            },
            {
                "internalType": "bytes32",
                "name": "toPair",
                "type": "bytes32"
            }
        ],
        "name": "isPairListed",
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
        "inputs": [
            {
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "oracle",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "_pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairFeed",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "",
                "type": "bytes32"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "_pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairLiquidationFeeP",
        "outputs": [
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
                "name": "_pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairMaxLeverage",
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
                "internalType": "uint16",
                "name": "_pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairMinLevPos",
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
                "name": "_pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairMinLeverage",
        "outputs": [
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
                "name": "_pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairOracleFee",
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
                "name": "_pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairOvernightMaxLeverage",
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
                "internalType": "uint16",
                "name": "pairIndex",
                "type": "uint16"
            }
        ],
        "name": "pairs",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "from",
                "type": "bytes32"
            },
            {
                "internalType": "bytes32",
                "name": "to",
                "type": "bytes32"
            },
            {
                "internalType": "bytes32",
                "name": "feed",
                "type": "bytes32"
            },
            {
                "internalType": "uint64",
                "name": "tradeSizeRef",
                "type": "uint64"
            },
            {
                "internalType": "uint32",
                "name": "overnightMaxLeverage",
                "type": "uint32"
            },
            {
                "internalType": "uint32",
                "name": "maxLeverage",
                "type": "uint32"
            },
            {
                "internalType": "uint8",
                "name": "groupIndex",
                "type": "uint8"
            },
            {
                "internalType": "uint8",
                "name": "feeIndex",
                "type": "uint8"
            },
            {
                "internalType": "string",
                "name": "oracle",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "_index",
                "type": "uint16"
            }
        ],
        "name": "pairsBackend",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "from",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "to",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "feed",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint64",
                        "name": "tradeSizeRef",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "overnightMaxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint8",
                        "name": "groupIndex",
                        "type": "uint8"
                    },
                    {
                        "internalType": "uint8",
                        "name": "feeIndex",
                        "type": "uint8"
                    },
                    {
                        "internalType": "string",
                        "name": "oracle",
                        "type": "string"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Pair",
                "name": "",
                "type": "tuple"
            },
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "name",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "minLeverage",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "maxCollateralP",
                        "type": "uint16"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Group",
                "name": "",
                "type": "tuple"
            },
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "name",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint64",
                        "name": "minLevPos",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "oracleFee",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint16",
                        "name": "liqFeeP",
                        "type": "uint16"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Fee",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "pairsCount",
        "outputs": [
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
                "name": "_pairIndex",
                "type": "uint16"
            }
        ],
        "name": "removePair",
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
                "internalType": "uint32",
                "name": "maxLeverage",
                "type": "uint32"
            }
        ],
        "name": "setPairMaxLeverage",
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
                "internalType": "uint32[]",
                "name": "values",
                "type": "uint32[]"
            }
        ],
        "name": "setPairMaxLeverageArray",
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
                "internalType": "uint32",
                "name": "overnightMaxLeverage",
                "type": "uint32"
            }
        ],
        "name": "setPairOvernightMaxLeverage",
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
                "internalType": "uint32[]",
                "name": "values",
                "type": "uint32[]"
            }
        ],
        "name": "setPairOvernightMaxLeverageArray",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint8",
                "name": "_id",
                "type": "uint8"
            },
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "name",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint64",
                        "name": "minLevPos",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint64",
                        "name": "oracleFee",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint16",
                        "name": "liqFeeP",
                        "type": "uint16"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Fee",
                "name": "_fee",
                "type": "tuple"
            }
        ],
        "name": "updateFee",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint8",
                "name": "_id",
                "type": "uint8"
            },
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "name",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint16",
                        "name": "minLeverage",
                        "type": "uint16"
                    },
                    {
                        "internalType": "uint16",
                        "name": "maxCollateralP",
                        "type": "uint16"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Group",
                "name": "_group",
                "type": "tuple"
            }
        ],
        "name": "updateGroup",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "_pairIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint256",
                "name": "_amount",
                "type": "uint256"
            },
            {
                "internalType": "bool",
                "name": "_long",
                "type": "bool"
            },
            {
                "internalType": "bool",
                "name": "_increase",
                "type": "bool"
            }
        ],
        "name": "updateGroupCollateral",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "_pairIndex",
                "type": "uint16"
            },
            {
                "components": [
                    {
                        "internalType": "bytes32",
                        "name": "from",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "to",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "feed",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "uint64",
                        "name": "tradeSizeRef",
                        "type": "uint64"
                    },
                    {
                        "internalType": "uint32",
                        "name": "overnightMaxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "maxLeverage",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint8",
                        "name": "groupIndex",
                        "type": "uint8"
                    },
                    {
                        "internalType": "uint8",
                        "name": "feeIndex",
                        "type": "uint8"
                    },
                    {
                        "internalType": "string",
                        "name": "oracle",
                        "type": "string"
                    }
                ],
                "internalType": "struct IOstiumPairsStorage.Pair",
                "name": "_pair",
                "type": "tuple"
            }
        ],
        "name": "updatePair",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
