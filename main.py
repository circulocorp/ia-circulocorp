from PydoNovosoft.utils import Utils
from PydoNovosoft.scope.mzone import MZone4
from time import sleep
import sys
import requests
import os
import json_logging
import logging
import pika
import json


json_logging.ENABLE_JSON_LOGGING = True
json_logging.init()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
config = Utils.read_config("package.json")

if os.environ is None or "environment" not in os.environ:
    env_cfg = config["dev"]
else:
    env_cfg = config[os.environ["environment"]]

url = env_cfg["API_URL"]
rabbitmq = env_cfg["RABBITMQ_URL"]

if env_cfg["secrets"]:
    mzone_user = Utils.get_secret("mzone_user")
    mzone_pass = Utils.get_secret("mzone_pass")
    rabbit_user = Utils.get_secret("rabbitmq_user")
    rabbit_pass = Utils.get_secret("rabbitmq_passw")
    api_pass = Utils.get_secret("token_key")
else:
    mzone_user = env_cfg["mzone_user"]
    mzone_pass = env_cfg["mzone_pass"]
    rabbit_user = env_cfg["rabbitmq_user"]
    rabbit_pass = env_cfg["rabbitmq_passw"]
    api_pass = env_cfg["token_key"]


def get_pool_false(vehicles):
    m = MZone4(mzone_user, mzone_pass)
    no_polling = []
    nvehicles = []
    ids = []
    for vehicle in vehicles:
        ids.append(vehicle["Id"])

    resp = m.get_poll_vehicles(ids).json()
    for id in ids:
        if not resp[id]:
            no_polling.append(id)
    for vehicle in vehicles:
        if vehicle["Id"] in no_polling:
            nvehicles.append(vehicle)
    return nvehicles


def mark_quarantine(vehicles):
    data = {"quarantine": 1}
    for v in vehicles:
        logger.info("Vehicle on quarantine",
                    extra={'props': {"app": config["name"], "label": config["name"], "vehicle": v}})
        requests.patch(url+"/api/vehicles/"+v["_id"], json=data)
        envelop = dict()
        envelop["message"] = "La unidad "+v["Description"]+" esta en cuarentena porque no ha reportado ubicacion"
        envelop["address"] = "525543593417"
        logger.info("Enviando mensaje", extra={'props': {"app": config["name"], "label": config["name"],
                                                         "message": envelop["message"], "address": envelop["address"]}})
        send_to_rabbit(envelop)


def send_to_rabbit(envelop):
    logger.info("Posting data to RabbitMQ", extra={'props': {"app": config["name"], "label": config["name"]}})
    credentials = pika.PlainCredentials(rabbit_user, rabbit_pass)
    parameters = pika.ConnectionParameters(rabbitmq, 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange='circulocorp', exchange_type='direct', durable=True)
    channel.basic_publish(exchange='circulocorp', routing_key='notificaciones',
                          body=json.dumps(envelop))


def start():
    vehicles = requests.get(url+"/api/vehicles/lastreport/5").json()
    ids = []
    for vehicle in vehicles:
        if not vehicle["quarantine"] or vehicle["quarantine"] == 0:
            ids.append(vehicle)
    ids = get_pool_false(ids)
    sleep(60)
    ids = get_pool_false(ids)
    mark_quarantine(ids)


def main():
    print(Utils.print_title("package.json"))
    while True:
        start()
        sleep(int(env_cfg["sleep"]))


if __name__ == '__main__':
    main()
