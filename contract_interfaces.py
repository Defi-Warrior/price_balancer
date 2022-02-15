import json
import os
from os.path import join


dir_path = os.path.dirname(os.path.realpath(__file__))


class Interface:
    with open(join(dir_path, "./abis", "ERC20.json"), "r") as f:
        ERC20 = json.load(f)

    with open(join(dir_path, "./abis", "Router.json"), "r") as f:
        ROUTER = json.load(f)
