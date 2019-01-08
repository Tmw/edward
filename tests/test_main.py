import unittest
from main import main
from unittest.mock import patch


class MainTest(unittest.TestCase):

    def test_slack_token_missing(self):
        with self.assertRaises(RuntimeError) as context:
            main()

        self.assertEqual("SLACK_TOKEN not set", str(context.exception))
