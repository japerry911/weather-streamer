import argparse
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import (PipelineOptions,
                                                  SetupOptions,
                                                  StandardOptions)


class LogResults(beam.DoFn):
    """Just log the results"""

    def process(self, element, **_kwargs):
        logging.info("Pub/Sub event: %s", element)
        yield element


def run(
    argv=None,
    save_main_session=True,
):
    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args(argv)

    input_subscription = "projects/weather-streamer/subscriptions/dataflow-subscription"

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    pipeline_options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=pipeline_options) as pipeline:
        messages = pipeline | "Read from PubSub" >> beam.io.ReadFromPubSub(
            subscription=input_subscription
        )

        lines = messages | "decode" >> beam.Map(lambda x: x.decode("utf-8"))

        # noinspection PyTypeChecker
        lines | "Log results" >> beam.ParDo(LogResults())


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
