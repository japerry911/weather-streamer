from datetime import datetime
import logging
from random import choice
from time import sleep

from faker import Faker
from google.cloud import pubsub_v1


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s :: %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    logger.info("Generating and Publishing Messages")
    generate_and_publish_messages(num=3, logger=logger)


def generate_and_publish_messages(num: int, logger: logging.Logger):
    fake = Faker()
    publisher = pubsub_v1.PublisherClient()
    topic_name = "projects/weather-streamer/topics/weather-streamer"

    for idx in range(num):
        logger.info(f"Publishing message #{idx + 1}")

        message = ",".join(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(fake.numerify()),
                str(fake.numerify()),
                choice(["1", "2"]),
            ]
        )

        future = publisher.publish(topic_name, message.encode("utf-8"))
        future.result()

        sleep(5)


if __name__ == "__main__":
    main()
