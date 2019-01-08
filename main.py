from edward import Edward
import os
import signal

DEFAULT_MAX_THREADS = 2


def main():
    token = os.getenv("SLACK_TOKEN")
    threads = os.getenv("THREADS", DEFAULT_MAX_THREADS)

    if token is None:
        raise RuntimeError("SLACK_TOKEN not set")

    edward = Edward(slack_token=token, max_threads=threads)

    stopper = lambda *args: edward.stop()
    signal.signal(signal.SIGINT, stopper)
    signal.signal(signal.SIGTERM, stopper)

    edward.start()


# Kick off main program
if __name__ == "__main__":
    main()
