from PydoNovosoft.utils import Utils
from PydoNovosoft.scope import MZone
import os
import json_logging
import logging


json_logging.ENABLE_JSON_LOGGING = True
json_logging.init()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_path = os.path.join('logs', 'ia-circulocorp.log')
logger.addHandler(logging.FileHandler(filename=log_path, mode='w'))
config = Utils.read_config("package.json")


def start():
    m = MZone("", "", "")
    vehicles = m.get_vehicles()
    for vehicle in vehicles:
        print(vehicle)


def main():
    print(Utils.print_title("package.json"))
    start()


if __name__ == '__main__':
    main()
