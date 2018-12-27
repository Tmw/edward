from slackclient import SlackClient
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import requests
from logger import EdwardLogger
from processor import process


# which filetypes are we reacting to
VALID_TYPES = ["JPG", "JPEG", "PNG"]
DEFAULT_MAX_THREADS = 2


class SlackWrapper:
    def __init__(self, token):
        self.token = token
        self.client = SlackClient(token)
        self.__should_quit = False
        self.__edward_id = None
        self.__workers = ThreadPoolExecutor(
            max_workers=DEFAULT_MAX_THREADS, thread_name_prefix="edward_worker"
        )

    def stop(self):
        EdwardLogger.info("Gracefully stopping Edward. Bye 👋")
        self.__should_quit = True
        self.__workers.shutdown(wait=True)

    def start(self):
        """
        Connect to Slacks real time messaging client and kick of the main loop
        """

        # first things first; let's connect to Slack RTM
        if self.client.rtm_connect(auto_reconnect=True, with_team_state=False):

            # once that succeeds, store our own user ID for filtering
            self.__edward_id = self.client.api_call("auth.test")["user_id"]

            # kick off main loop; blocking
            self.run_main_loop()

    def run_main_loop(self):
        """
        The main loop is responsible for reading messages off of the queue
        and kicking off converting jobs should a message be applicable.
        """

        EdwardLogger.info("Ready for action 💪")

        # start looping as long as we're connected
        while self.client.server.connected:
            # should we shutdown?
            if self.__should_quit:
                break

            batch = self.client.rtm_read()
            job_params = self.extract_job_params(batch)

            if job_params is not None:
                # all is OK, spawn handler
                download_url, response_channel_id = job_params

                # add job to threaded worker pool so we can continue
                # accepting new work in the main thread
                self.__workers.submit(
                    self.handle_file, download_url, response_channel_id
                )

            # no matter if we scheduled a job or not; wait a bit
            time.sleep(1)

    def extract_job_params(self, messages):
        """
        extract_job_params takes the original slack message and returns either
        `None` or a tuple containing the `download_url` and `return_channel_id`:

        * download_url is a string containing the download location
        * return_channel_id is the Slack channel id on which to reply to
        """

        # if there's no messages to be polled, we receive an empty list.
        # we should just skip and try again
        if len(messages) == 0:
            return None

        # the messages are returned in an array; grab the first one
        # and start validating the payload
        message = messages[0]

        # if message does not contain required fields, ignore it
        if not is_message_valid(message):
            return None

        # if message author is edward itself, ignore to avoid endless looping
        if message["user"] == self.__edward_id:
            return None

        # if it isn't a file_shared message, just ignore and continue
        if not is_file_attached(message):
            return None

        # if there is a file but it is not supported by Edward
        file = message["files"][0]
        if not is_file_valid(file):
            EdwardLogger.info("Attached file not of valid type, skipping")
            return None

        # if we've reached this point, we encountered a valid message.
        # extract the important bits and return a tuple containing job params
        return (file["url_private_download"], message["channel"])

    def handle_file(self, download_url, response_channel_id):
        """
        handle_file takes care of downloading the file, running it through
        the image processor and uploading it to the originating Slack channel.
        """

        EdwardLogger.info("File attached and valid, handling in")

        response = requests.get(download_url, headers=self.__get_http_headers())
        if response.ok:
            EdwardLogger.info("Downloaded file, start converting..")
            img = Image.open(BytesIO(response.content))
            processed = process(img)

            EdwardLogger.info("File processed, uploading to Slack")

            # store image as bytes array and rewind
            output_bytes = BytesIO()
            processed.save(output_bytes, format="PNG")
            output_bytes.seek(0)

            # upload processed image to Slack
            slack_response = self.client.api_call(
                "files.upload",
                channels=response_channel_id,
                file=output_bytes,
                title=":thumbsup:",
            )

            if slack_response["ok"]:
                EdwardLogger.info("Uploaded processed image succesfully")
            else:
                err = slack_response["error"]
                EdwardLogger.info("Error uploading to slack: {}".format(err))

            EdwardLogger.info("Done")

    def __get_http_headers(self):
        return {"Authorization": "Bearer {}".format(self.token)}


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

