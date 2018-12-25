from slack import SlackWrapper
import os
import signal


# def handle_sigterm(_signum, _frame):
#     global stopped
#     stopped = True


def main():
    # signal.signal(signal.SIGINT, handle_sigterm)
    # signal.signal(signal.SIGTERM, handle_sigterm)

    token = os.environ["SLACK_TOKEN"]
    slack_wrapper = SlackWrapper(token)
    slack_wrapper.start()


# Kick off main program
if __name__ == "__main__":
    main()
