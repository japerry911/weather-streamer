terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  credentials = file("../credentials.json")

  project = "weather-streamer"
  region  = "us-central1"
  zone    = "us-central1-a"
}

resource "google_storage_bucket" "dataflow_gcs_bucket" FAIL_AHHH {
  name     = "dataflow-bucket-123214324"
  location = "us-central1"
}

resource "google_pubsub_topic" "weather_streamer_topic" {
  name = "weather-streamer"
}

resource "google_pubsub_subscription" "dataflow_subscription" {
  name  = "dataflow-subscription"
  topic = google_pubsub_topic.weather_streamer_topic.name
}

resource "google_bigquery_dataset" "streaming_data" {
  dataset_id  = "streaming_data"
  location    = "us-central1"
  description = "Weather Streaming Data dataset"
}

resource "google_bigquery_table" "home_weather_data" {
  dataset_id = google_bigquery_dataset.streaming_data.dataset_id
  table_id   = "home_weather_data"

  schema = <<EOF
[
  {
    "name": "datetime_fetched",
    "type": "DATETIME",
    "mode": "NULLABLE",
    "description": "The Datetime that the data was fetched/gathered"
  },
  {
    "name": "temperature",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "The temperature data in fahrenheit"
  },
  {
    "name": "humidity",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "The humidity data"
  },
  {
    "name": "pi_id",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The ID for the Raspberry Pi, the data gatherer"
  }
]
EOF
}

resource "google_dataflow_job" "weather_streaming_dataflow_job" {
  name              = "weather-streaming-dataflow-job"
  temp_gcs_location = "gs://dataflow-bucket-123214324/temp"
  max_workers       = 1
  machine_type      = "n1-standard-1"
  region            = "us-central1"
  template_gcs_path = "gs://dataflow-bucket-123214324/templates/weather_streamer_template.py"
}
