import argparse
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import (
    PipelineOptions,
    SetupOptions,
    StandardOptions,
)


class PrepareDataForBigQuery(beam.DoFn):
    """Prepare Pub/Sub data for BigQuery"""

    def process(self, element, **_kwargs):
        """Split the data into individual values"""
        sub_elements = element.split(",")

        yield {
            "datetime_fetched": sub_elements[0],
            "temperature": float(sub_elements[1]),
            "humidity": float(sub_elements[2]),
            "pi_id": sub_elements[3],
        }


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

    bq_schema_str = (
        "datetime_fetched:DATETIME,temperature:FLOAT,humidity:FLOAT,pi_id:STRING"
    )

    table_ref = "weather-streamer:streaming_data.home_weather_data"

    with beam.Pipeline(options=pipeline_options) as pipeline:
        # noinspection PyTypeChecker
        (
            pipeline
            | "Read from PubSub"
            >> beam.io.ReadFromPubSub(subscription=input_subscription)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "Prepare for BigQuery" >> beam.ParDo(PrepareDataForBigQuery())
            | "Write to BigQuery"
            >> beam.io.WriteToBigQuery(
                table_ref,
                schema=bq_schema_str,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            )
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
