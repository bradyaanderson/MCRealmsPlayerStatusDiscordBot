import os

from dotenv import load_dotenv

from realmsAPI import RealmsAPI
from statusBot import StatusBotClient

if __name__ == '__main__':
    load_dotenv()
    realms_api = RealmsAPI()
    client = StatusBotClient(realms_api)
    client.run(os.getenv("TOKEN"))
