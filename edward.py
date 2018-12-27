from concurrent.futures import ThreadPoolExecutor
from slack import SlackWrapper
from logger import EdwardLogger
from processor import process
from PIL import Image
from io import BytesIO


class Edward:
    DEFAULT_MAX_THREADS = 2

    def __init__(self, slack_token=None, max_threads=DEFAULT_MAX_THREADS):
        self.__slack_wrapper = SlackWrapper(
            token=slack_token,
            on_file_shared_fn=self.on_file_shared
        )

        self.__worker_queue = ThreadPoolExecutor(
            max_workers=max_threads,
            thread_name_prefix="edward_worker"
        )

    def stop(self):
        EdwardLogger.info("Gracefully stopping Edward. Bye 👋")
        self.__slack_wrapper.stop()
        self.__worker_queue.shutdown(wait=True)

    def start(self):
        self.__slack_wrapper.start()

    def on_file_shared(self, download_url, response_channel_id):
        """
        This callback is fired when the slack_wrapper found a shared image
        that is elligible for processing. It grabs the params and schedules the
        processing job in a background thread.
        """

        self.__worker_queue.submit(
            self.handle_file, download_url, response_channel_id
        )

    def handle_file(self, download_url, response_channel_id):
        """
        handle_file takes care of downloading the file, running it through
        the image processor and uploading it to the originating Slack channel.

        This method is calld from the ThreadPoolExecutor so it does not block
        the main thread while doing async io.
        """

        response = self.__slack_wrapper.download_image(download_url)
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
            error = self.__slack_wrapper.upload_image(
                response_channel_id, output_bytes
            )

            if error is not None:
                EdwardLogger.info("Error uploading to slack: {}".format(err))
            else:
                EdwardLogger.info("Uploaded processed image successfully")

            EdwardLogger.info("Done")
