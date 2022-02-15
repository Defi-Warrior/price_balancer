import eth_account
from web3 import Web3


class ContractHelper:
    def __init__(self, web3, private_key: str, network: str):
        self.web3 = web3
        self.account = eth_account.Account.from_key(private_key)
        self.private_key = private_key
        self.chain_id = 56 if network == "mainnet" else 97
        self.default_gasprice = Web3.toWei('6', 'gwei') if network == "mainnet" else Web3.toWei('10', 'gwei')
        self.address = self.account.address

    def deployed(self, interface, address):
        if "abi" in interface:
            return self.web3.eth.contract(abi=interface["abi"], address=address)
        return self.web3.eth.contract(abi=interface, address=address)

    def new_contract(self, interface, constructor_params, address=""):
        print("Init contract with params: ", constructor_params)
        if address:
            return self.web3.eth.contract(abi=interface["abi"], address=address)

        contract = self.web3.eth.contract(abi=interface["abi"], bytecode=interface["bytecode"])

        tx = contract.constructor(*constructor_params).buildTransaction({
            'chainId': self.chain_id,
            'gasPrice': self.default_gasprice,
            'nonce': self.web3.eth.get_transaction_count(self.account.address),
            'from': self.account.address
        })

        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return self.web3.eth.contract(tx_receipt.contractAddress, abi=interface['abi'])

    def run_func(self, contract, func_name, params, wait=True, value=0):
        print(f"executing: {func_name} with params: {params}")
        transaction = contract.functions[func_name](*params)
        gas = transaction.estimateGas({'from': self.account.address, 'value': value})
        tx = contract.functions[func_name](*params).buildTransaction({
            'chainId': self.chain_id,
            'gasPrice': self.default_gasprice,
            'gas': int(gas * 1.2),
            'nonce': self.web3.eth.get_transaction_count(self.account.address),
            'from': self.account.address,
            'value': value
        })

        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        if wait:
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status != 1:
                raise ValueError("Transaction failed")
            return tx_receipt.transactionHash

        return tx_hash
