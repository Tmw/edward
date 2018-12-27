from slack import SlackWrapper
import os
import signal

DEFAULT_MAX_THREADS = 2


def main():
    token = os.getenv("SLACK_TOKEN")
    threads = os.getenv("THREADS", DEFAULT_MAX_THREADS)

    slack_wrapper = SlackWrapper(token, max_threads=threads)

    stopper = lambda *args: slack_wrapper.stop()
    signal.signal(signal.SIGINT, stopper)
    signal.signal(signal.SIGTERM, stopper)

    slack_wrapper.start()


# Kick off main program
if __name__ == "__main__":
    main()
