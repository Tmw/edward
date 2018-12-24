from PIL import Image
from io import BytesIO
from slackclient import SlackClient
import time
import requests
import os

from processor import process

# which filetypes are we reacting to
VALID_TYPES = ["JPG", "JPEG", "PNG"]


def is_message_valid(message):
    return "type" in message and message["type"] == "message" and "user" in message


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
    edward_id = None
    dir(client)

    if client.rtm_connect(auto_reconnect=True, with_team_state=False):
        edward_id = client.api_call("auth.test")["user_id"]

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

            # if message does not contain required fields, ignore it
            if not is_message_valid(msg):
                continue

            # if message author is edward itself, ignore to avoid endless looping
            if msg["user"] == edward_id:
                continue

            # if it isn't a file_shared message, just ignore and continue
            if not is_file_attached(msg):
                continue

            # if there is a file but it is not supported by Edward
            file = msg["files"][0]
            if not is_file_valid(file):
                print("Attached file not of valid type, skipping")
                continue

            # TODO: The actual image downloading, processing and uploading
            # is probably something we'd want to offload in a separate thread
            # so that we can continue accepting jobs on the main thread.

            # TODO: We probably want to do some signal interception that
            # neatly stops polling and closes the RTM connection. Now, when we
            # do CTRL + C we're getting hit with a ton of weird errors :)

            print("File attached and valid, downloading...")

            url = file["url_private_download"]
            headers = {"Authorization": "Bearer {}".format(token)}
            response = requests.get(url, headers=headers)
            if response.ok:
                print("Downloaded file, start converting..")
                img = Image.open(BytesIO(response.content))
                processed = process(img)

                print("File processed, uploading to Slack")

                # store image as bytes array and rewind
                output_bytes = BytesIO()
                processed.save(output_bytes, format="PNG")
                output_bytes.seek(0)

                # upload processed image to Slack
                response_channel_id = msg["channel"]
                slack_response = client.api_call(
                    "files.upload",
                    channels=response_channel_id,
                    file=output_bytes,
                    title=":thumbsup:",
                )
                if slack_response["ok"]:
                    print("Uploaded processed image succesfully")
                else:
                    err = slack_response["error"]
                    print("Error uploading to slack: {}".format(err))

                print("Done")

            time.sleep(1)


# Kick off main program
if __name__ == "__main__":
    main()
