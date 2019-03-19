import PeriodicPositionProto_pb2
from google.protobuf.json_format import MessageToJson
import requests
from datetime import datetime
import json
import base64


class MProfiler(object):

    def __init__(self, url, user="", passw=""):
        self._profiler = url
        self._username = user
        self._password = passw

    def get_messages(self):
        url = self._profiler+"/v1/MessageBatch"
        obj = requests.get(url, auth=(self._username, self._password))
        batch = {}
        if obj is not None and obj.status_code == 200:
            res = obj.json()
            events = []
            for message in res["messages"]:
                event = PeriodicPositionProto_pb2.PeriodicPosition()
                binary = base64.b64decode(message["body"])
                event.ParseFromString(str(binary))
                parsed = json.loads(MessageToJson(event, False, False, 0))
                events.append(parsed)
            batch["events"] = events
            batch["batchId"] = res["batchId"]
            batch["date"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return batch

    def acknowledge(self, batch):
        url = self._profiler + "/v1/MessageBatch/Ack/"+batch
        obj = requests.post(url, auth=(self._username, self._password))
        if obj.status_code == 200:
            return True
        else:
            return False

