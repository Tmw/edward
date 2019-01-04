import unittest
from slack import SlackWrapper


class SlackTest(unittest.TestCase):

    def setUp(self):
        self.slack_wrapper = SlackWrapper(token="NotInterresting")

    def test_extract_job_params(self):
        # assert happy path
        valid_msg = _generate_valid_message()
        url, chan_id = self.slack_wrapper.extract_job_params([valid_msg])

        self.assertEqual(url, "http://some-download-url.com")
        self.assertEqual(chan_id, "some_channel_id")

        # assert empty messages
        self.assertEqual(None, self.slack_wrapper.extract_job_params([]))

        # assert early return when message is from Edward itself
        self.slack_wrapper._SlackWrapper__edward_id = "edward_id"
        msg = dict(type="message", user="edward_id")
        self.assertEqual(None, self.slack_wrapper.extract_job_params([msg]))

        # assert early return when no file attached
        msg = dict(type="message", user="another_user_id")
        self.assertEqual(None, self.slack_wrapper.extract_job_params([msg]))

        msg = dict(
            type="message",
            user="another_user_id",
            files=[dict(pretty_type="wav")]
        )
        self.assertEqual(None, self.slack_wrapper.extract_job_params([msg]))


def _generate_valid_message():
    return dict(
        type="message",
        user="some_user_id",
        channel="some_channel_id",
        files=[_generate_valid_file()]
    )


def _generate_valid_file():
    return dict(
        pretty_type="jpeg",
        url_private_download="http://some-download-url.com"
    )
