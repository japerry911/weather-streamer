# Weather-Streamer

## Description
This project utilizes multiple Raspberry Pi Pico W's to collect weather data and publish it to Google Cloud Pub/Sub every 30 seconds.
Once published to Google Cloud Pub/Sub the data is processed by Google Cloud DataFlow and landed to Google Cloud BigQuery.

## Hardware
- 2 Raspberry Pi Pico W
- 2 Si7021 Temperature, and Humidity Sensors (Adafruit)
- 2 Micro USB Power Cords for the Pis
- 2 Jumper Wires (for connecting Pis to sensors)

## Software for Pis
- [Thonny IDE](https://thonny.org/) (for flashing the Raspberry Pi Pico W's)
- MicroPython
- URequests
- MicroPython_Base64 Library
- MicroPython_Si7021 Library

## Software for Streamer
- Google Cloud SDK
- Apache Beam SDK
- Python 3.10
- Google Cloud Pub/Sub
- Google Cloud DataFlow
- Google Cloud BigQuery
- Google Cloud Storage
