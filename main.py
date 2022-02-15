import argparse
import configparser
import math
import os
import random
import time

from web3 import Web3

from config import Config
from contract_helper import ContractHelper
from contract_interfaces import Interface


def read_config(network: str) -> Config:
    parser = configparser.ConfigParser()
    parser.read("config.ini")

    config_section = parser[network]

    cfg = Config()
    cfg.ROUTER_ADDRESS = config_section["ROUTER"]
    cfg.BUSD_ADDRESS = config_section["BUSD"]
    cfg.CWIG_ADDRESS = config_section["CWIG"]
    cfg.CWIG_BUSD_LP_ADDRESS = config_section["CWIG_BUSD_LP"]
    cfg.web3 = Web3(Web3.HTTPProvider(config_section["PROVIDER"]))

    while not cfg.web3.isConnected():
        print("Could not connect to: ", config_section["PROVIDER"], "retry in 30 seconds")
        time.sleep(30)

    return cfg


def expand_to_18_decimals(value: int):
    return value * 10**18


def run(arg: dict, cfg: Config):
    contract = ContractHelper(cfg.web3, os.environ.get("PRIVATE_KEY"), arg["network"])

    router = contract.deployed(Interface.ROUTER, cfg.ROUTER_ADDRESS)

    lp_pair = contract.deployed(Interface.LP_PAIR, cfg.CWIG_BUSD_LP_ADDRESS)

    token0 = lp_pair.functions.token0().call()

    if token0 == cfg.BUSD_ADDRESS:
        busd_reserve, cwig_reserve, _ = lp_pair.functions.getReserves().call()
    else:
        cwig_reserve, busd_reserve, _ = lp_pair.functions.getReserves().call()

    current_price = busd_reserve / cwig_reserve
    k = busd_reserve * cwig_reserve
    target_price = random.uniform(arg["low_price"], arg["high_price"])
    print(f"new target price: {target_price}")

    if current_price < float(arg["low_price"]):
        new_busd_reserve = int(math.sqrt(k*target_price))
        if new_busd_reserve < busd_reserve:
            print(f"current price is : {current_price}, no need to buy")
            return

        amount_in = new_busd_reserve - busd_reserve

        if amount_in > expand_to_18_decimals(3000):
            amount_in = expand_to_18_decimals(3000)

        amount_out = int(router.functions.getAmountsOut(amount_in, [cfg.BUSD_ADDRESS, cfg.CWIG_ADDRESS]).call()[1] * 0.99)

        print(f"Buy {amount_in//10**18}$ cwig at price: {current_price}")
        contract.run_func(router, "swapExactTokensForTokens", [amount_in, amount_out, [cfg.BUSD_ADDRESS, cfg.CWIG_ADDRESS], contract.address, int(time.time() + 60*10)])
    elif current_price > float(arg["high_price"]):
        new_cwig_reverse = int(math.sqrt(k/target_price))

        if new_cwig_reverse < cwig_reserve:
            print(f"current price is : {current_price}, no need to sell")
            return

        amount_in = new_cwig_reverse - cwig_reserve
        amount_out = int(router.functions.getAmountsOut(amount_in, [cfg.CWIG_ADDRESS, cfg.BUSD_ADDRESS]).call()[1] * 0.99)

        print(f"Sell {amount_in//10**18} cwig at price: {current_price}")
        contract.run_func(router, "swapExactTokensForTokens", [amount_in, amount_out, [cfg.CWIG_ADDRESS, cfg.BUSD_ADDRESS], contract.address, int(time.time() + 60*10)])


if __name__ == '__main__':
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("low_price", type=float, help="lower bound of cwig-busd price")
    arg_parse.add_argument("high_price", type=float, help="upper bound of cwig-busd price")
    arg_parse.add_argument("--network", type=str, required=False, default="testnet", choices=["mainnet", "testnet"],
                           help="which network to run")
    arg_parse.add_argument("--interval", type=int, required=False, default=3600,
                           help="bot will check price after 'interval' time has passed")

    args = vars(arg_parse.parse_args())

    config = read_config(args["network"])

    while True:
        run(args, config)
        time.sleep(args["interval"])
