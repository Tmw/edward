import unittest
from edward import Edward as EdwardClass
from unittest.mock import patch
import logging


class EdwardTest(unittest.TestCase):

    @patch('processor.prepare')
    @patch('edward.SlackWrapper')
    @patch('edward.ThreadPoolExecutor')
    def setUp(
        self,
        MockThreadPoolExecutor,
        MockSlackWrapper,
        MockPrepare
    ):
        # suppress log messages
        logging.disable(logging.INFO)

        self.edwardInstance = EdwardClass(
            slack_token="not_important"
        )

        self.mocks = dict(
            thread_pool_executor=MockThreadPoolExecutor.return_value,
            slack_wrapper=MockSlackWrapper.return_value,
        )

    def test_start(self):
        """
        assert that a call to start actually calls start on the slack wrapper
        """

        self.edwardInstance.start()
        assert self.mocks['slack_wrapper'].start.called

    def test_stop(self):
        """
        assert that a call to stop actually stops the SlackWrapper and shuts
        down the internal worker queue.
        """

        self.edwardInstance.stop()

        assert self.mocks['thread_pool_executor'].shutdown.called
        assert self.mocks['slack_wrapper'].stop.called

    def test_on_file_shared(self):
        """
        assert that on_file_shared actually schedules an internal job
        """

        download_url = "http://fake.url"
        response_channel_id = "fake_chan_id"

        self.edwardInstance.on_file_shared(download_url, response_channel_id)

        self.mocks['thread_pool_executor'].submit.assert_called_with(
            self.edwardInstance.handle_file,
            download_url,
            response_channel_id
        )
