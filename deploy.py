from solcx import compile_standard, install_solc
from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()


install_solc("0.8.11")

# Compile solidity smart contract
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.11",
)

with open("compile_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connecting to rinkby network
# https://trufflesuite.com/ganache/
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/93ab81115564422ab90ffc2b1d271251")
)
chain_id = 4
my_address = "0x409E3918c8C31c7FA62Cca51e4529fbdBbe5fA64"
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
    }
)


# 2. sign a transaction
sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)

print("Deploying contract...")

# 3. send a transaction
send_transaction = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
transaction_receipt = w3.eth.wait_for_transaction_receipt(send_transaction)

print("Deployed!")

# Working with contract
# We need contract address
# We need contract ABI
simple_storage = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)

print(simple_storage.functions.retrieve().call())

print("Updating contract...")

"""
 Call
"""
# build and store transaction
store_transaction = simple_storage.functions.store(1000).buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
        "gasPrice": w3.eth.gas_price,
    }
)

# store and sign transaction
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

# store and send transaction
send_store_txn = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)

# receipt
tx_receipt_store = w3.eth.wait_for_transaction_receipt(send_store_txn)

print(simple_storage.functions.retrieve().call())
