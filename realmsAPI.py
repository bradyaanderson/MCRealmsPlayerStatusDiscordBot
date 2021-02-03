import json
import os

import requests


class RealmsAPI:
    AUTH_URL_BASE = "https://authserver.mojang.com"
    REALMS_URL_BASE = "https://pc.realms.minecraft.net"

    def __init__(self):
        self.email = os.getenv("MC_EMAIL")
        self.password = os.getenv("MC_PASSWORD")
        self.username = os.getenv("MC_USERNAME")
        self.uuid = os.getenv("MC_UUID")
        self.version = os.getenv("MC_VERSION")
        self.world_id = os.getenv("MC_WORLD_ID")
        self.access_token = ""
        self.last_player_statuses = {}

        if not self.try_authenticate():
            raise AuthenticationError('Unable to authenticate.')

    def update_player_statuses(self):
        new_player_statues = self.get_player_status()
        status_updates = {}
        for player_name, status in new_player_statues.items():
            if not player_name in self.last_player_statuses or self.last_player_statuses[player_name] != status:
                status_updates[player_name] = status
        self.last_player_statuses = new_player_statues
        return status_updates

    def get_player_status(self):
        response = self.try_get_world()
        players = response["players"]

        player_statuses = {}
        for player in players:
            player_name = player["name"]
            player_statuses[player_name] = player["online"]
        return player_statuses

    def try_get_world(self, retries=2):
        for attempt in range(retries):
            response = self.get_world()
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401 and not self.try_authenticate():
                return False
            print("Failed to obtain world. Attempt: " + str(attempt), response.status_code)
        return False

    def get_world(self):
        url = self.REALMS_URL_BASE + '/worlds/' + self.world_id
        return self.get(url)

    def try_authenticate(self, retries=2):
        for attempt in range(retries):
            response = self.authenticate()
            if response.status_code == 200:
                response_json = response.json()
                self.access_token = response_json["accessToken"]
                return True
            print("Failed to obtain access token. Attempt: " + str(attempt))
        return False

    def authenticate(self):
        url = self.AUTH_URL_BASE + '/authenticate'
        payload = {
            "username": self.email,
            "password": self.password
        }
        return self.post(url, payload)

    def build_cookie(self):
        return "sid=token:{access_token}:{uuid};user={username};version={version}".format(
            access_token=self.access_token,
            uuid=self.uuid,
            username=self.username,
            version=self.version)

    def get(self, url):
        headers = {
            'Cookie': self.build_cookie()
        }
        return requests.request("GET", url, headers=headers, data={})

    def post(self, url, data):
        headers = {
            'Content-Type': 'application/json'
        }
        data_json = json.dumps(data)
        return requests.request("POST", url=url, headers=headers, data=data_json)


class AuthenticationError(Exception):
    def __init__(self, message):
        self.message = message
