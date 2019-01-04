from slackclient import SlackClient
from logger import EdwardLogger
import time
import requests


class SlackWrapper:
    DEFAULT_SUPPORTED_FILE_TYPES = ["jpg", "jpeg", "png"]

    def __init__(
        self,
        token=None,
        on_file_shared_fn=None,
        supported_file_types=DEFAULT_SUPPORTED_FILE_TYPES,
    ):
        """
        SlackWrapper handles communication with the Slack RTM and Web APIs

        Params:
        `slack_token` : String,
        `supported_file_types` a list of supported file types
        `on_file_shared_fn` : Fn(string, string) -> None - handle files
        """

        self.__token = token
        self.__client = SlackClient(token)
        self.__should_quit = False
        self.__edward_id = None
        self.__supported_file_types = supported_file_types
        self.__on_file_shared_fn = on_file_shared_fn

    def stop(self):
        self.__should_quit = True

    def start(self):
        """
        Connect to Slacks real time messaging client and kick of the main loop
        """

        # first things first; let's connect to Slack RTM
        if self.__client.rtm_connect(auto_reconnect=True, with_team_state=False):

            # once that succeeds, store our own user ID for filtering
            self.__edward_id = self.__client.api_call("auth.test")["user_id"]

            # kick off main loop; blocking
            self.run_main_loop()

    def run_main_loop(self):
        """
        The main loop is responsible for reading messages off of the queue
        and kicking off converting jobs should a message be applicable.
        """

        EdwardLogger.info("Ready for action 💪")

        # start looping as long as we're connected
        while self.__client.server.connected:
            # should we shutdown?
            if self.__should_quit:
                break

            batch = self.__client.rtm_read()
            job_params = self.extract_job_params(batch)

            if job_params is not None:
                # all is OK, spawn handler
                download_url, response_channel_id = job_params

                # perform the callback containing the job parameters
                EdwardLogger.info("File attached and valid")
                self.__on_file_shared_fn(download_url, response_channel_id)

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
        if not self.__is_message_valid(message):
            return None

        # if message author is edward itself, ignore to avoid endless looping
        if message["user"] == self.__edward_id:
            return None

        # if it isn't a file_shared message, just ignore and continue
        if not self.__is_file_attached(message):
            return None

        # if there is a file but it is not supported by Edward
        file = message["files"][0]
        pretty_type = file["pretty_type"].lower()
        if pretty_type not in self.__supported_file_types:
            EdwardLogger.info("Attached file not of valid type, skipping")
            return None

        # if we've reached this point, we encountered a valid message.
        # extract the important bits and return a tuple containing job params
        return (file["url_private_download"], message["channel"])

    def download_image(self, image_download_url):
        """
        download_file accepts a file_download_url, provides authorization
        and kicks off the request to Slack Web API
        """
        return requests.get(image_download_url, headers=self.__get_http_headers())

    def upload_image(self, channel_id, bytes):
        """
        upload_image uploads the sequence of bytes to the provided slack channel.
        It returns either None if all went well, or the error if something blew up
        """

        response = self.__client.api_call(
            "files.upload", channels=channel_id, file=bytes
        )

        if response["ok"]:
            return None
        else:
            return response["error"]

    def __get_http_headers(self):
        return {"Authorization": "Bearer {}".format(self.__token)}

    def __is_message_valid(self, message):
        return (
            "type" in message
            and message["type"] == "message"
            and "user" in message
        )

    def __is_file_attached(self, message):
        return (
            message["type"] == "message"
            and "files" in message
            and len(message["files"]) > 0
        )
