import argparse
import configparser

from config import Config


def read_config(network: str) -> Config:
    parser = configparser.ConfigParser()
    parser.read("config.ini")

    config_section = parser[network]

    cfg = Config()
    cfg.ROUTER_ADDRESS = config_section["ROUTER"]
    cfg.BUSD_ADDRESS = config_section["BUSD"]
    cfg.CWIG_ADDRESS = config_section["CWIG"]
    cfg.CWIG_BUSD_LP_ADDRESS = config_section["CWIG_BUSD_LP"]

    return cfg


def run(arg: dict, cfg: Config):
    pass


if __name__ == '__main__':
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("low_price", type=float, help="lower bound of cwig-busd price")
    arg_parse.add_argument("high_price", type=float, help="upper bound of cwig-busd price")
    arg_parse.add_argument("--network", type=str, required=False, default="testnet", choices=["mainnet", "testnet"],
                           help="which network to run")

    args = vars(arg_parse.parse_args())
    config = read_config(args["network"])

    run(args, config)

    print(args)
    print(config.ROUTER_ADDRESS, config.CWIG_ADDRESS, config.BUSD_ADDRESS, config.CWIG_BUSD_LP_ADDRESS)
