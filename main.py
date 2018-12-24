from PIL import Image
from io import BytesIO
from slackclient import SlackClient
import time
import requests
import os

from processor import process

# which filetypes are we reacting to
VALID_TYPES = ["JPG", "JPEG", "PNG"]


def is_file_attached(message):
    return (
        message["type"] == "message"
        and "files" in message
        and len(message["files"]) > 0
    )


def is_file_valid(file_object):
    return file_object["pretty_type"] in VALID_TYPES


def main():
    token = os.environ["SLACK_TOKEN"]
    client = SlackClient(token)

    if client.rtm_connect(auto_reconnect=True, with_team_state=False):
        print("Ready for action 💪")
        while client.server.connected:
            msgs = client.rtm_read()
            # if there's no messages to be polled, we receive an empty list.
            # we should just skip and try again
            if len(msgs) == 0:
                continue

            # the messages are returned in an array; grab the first one
            # and start validating the payload
            msg = msgs[0]

            # if it isn't a file_shared message, just ignore and continue
            if not is_file_attached(msg):
                continue

            # if there is a file but it is not supported by Edward
            file = msg["files"][0]
            if not is_file_valid(file):
                print("Attached file not of valid type, skipping")
                continue

            print("File attached and valid, downloading...")

            url = file["url_private_download"]
            headers = {"Authorization": "Bearer {}".format(token)}
            response = requests.get(url, headers=headers)
            if response.ok:
                img = Image.open(BytesIO(response.content))
                processed = process(img)
                # processed.show()

                # TODO: re-upload processed image back to user

            time.sleep(1)


# Kick off main program
if __name__ == "__main__":
    main()
