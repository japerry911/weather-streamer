from time import sleep

from faker import Faker
from google.cloud import pubsub_v1


def main():
    messages = generate_messages(num=1)
    publish_messages(messages=messages)


def publish_messages(messages: list[str]):
    publisher = pubsub_v1.PublisherClient()
    topic_name = "projects/weather-streamer/topics/weather-streamer"

    for message in messages:
        future = publisher.publish(topic_name, message.encode("utf-8"))
        future.result()


def generate_messages(num: int) -> list[str]:
    fake = Faker()
    messages = []

    for _ in range(num):
        messages.append(str(fake.numerify()))
        sleep(3)

    return messages


if __name__ == "__main__":
    main()
