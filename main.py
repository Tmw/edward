from slack import SlackWrapper
import os
import signal


def main():
    token = os.environ["SLACK_TOKEN"]
    slack_wrapper = SlackWrapper(token)

    stopper = lambda *args: slack_wrapper.stop()
    signal.signal(signal.SIGINT, stopper)
    signal.signal(signal.SIGTERM, stopper)

    slack_wrapper.start()


# Kick off main program
if __name__ == "__main__":
    main()
