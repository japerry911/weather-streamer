import logging
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

    logger.info("Generating messages")
    messages = generate_messages(num=1_000)

    logger.info("Publishing messages")
    publish_messages(messages=messages, logger=logger)


def publish_messages(messages: list[str], logger: logging.Logger):
    publisher = pubsub_v1.PublisherClient()
    topic_name = "projects/weather-streamer/topics/weather-streamer"

    for idx, message in enumerate(messages):
        logger.info(f"Publishing Message {idx + 1}/{len(messages)}")
        future = publisher.publish(topic_name, message.encode("utf-8"))
        future.result()
        sleep(3)


def generate_messages(num: int) -> list[str]:
    fake = Faker()
    messages = []

    for _ in range(num):
        messages.append(str(fake.numerify()))

    return messages


if __name__ == "__main__":
    main()
