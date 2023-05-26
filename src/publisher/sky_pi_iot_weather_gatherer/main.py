import json
from base64 import b64encode
from time import sleep, sleep_ms

import machine
import network
import urequests as requests
from si7021 import SI7021


class SkyPiStreamer:
    # ---Google Cloud Platform---
    GCP_PUBSUB_TOPIC_NAME = "<REDACTED>"
    GCP_PUBSUB_PUBLISH_URL = "<REDACTED>"
    GCP_CLIENT_ID = "<REDACTED>"
    GCP_CLIENT_SECRET = "<REDACTED>"
    GCP_REFRESH_TOKEN = "<REDACTED>"

    # ---Misc.---
    RASPBERRY_PI_PICO_W_ID = "raspberry-pi-pico-w-1"
    # ToDo: REDACT BEFORE VC PUSH
    WIFI_NAME = "<REDACTED>"
    WIFI_PASSWORD = "<REDACTED>"

    def __init__(self):
        pass

    def stream(self):
        # ~~~Be a meterologist forever~~~
        # ,--.::::::::::::::::::::::::::::::::::::....:::::::
        #     )::::::::::::::::::::::::::::::::..      ..::::
        #   _'-. _:::::::::::::::::::::::::::..   ,--.   ..::
        #  (    ) ),--.::::::::::::::::::::::.   (    )   .::
        #              )-._::::::::::::::::::..   `--'   ..::
        # _________________):::::::::::::::::::..      ..::::
        # ::::::::::::::::::::::::::::::::::::::::....:::::::
        # ::::::::: :: A drip of water... :::::::::::::::::::
        # :::::::: c> :::::::::::::::::::::::::::::::::::::::
        # !:!:!:!:<(; !:!:!:!:!:!:!:!:!:!:!:!:!:!:!:!:!:!:!:!
        # !!!!!!!! /\ !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # |!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|!|
        # |||||||||||||||||||||||||||||||||||||||||||||||||||
        # I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I|I
        # IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
        #

        led = machine.Pin("LED", machine.Pin.OUT)
        led.on()

        try:
            # Connect to WiFi
            self.connect_to_wifi()

            # Declare machines
            i2c = machine.I2C(0)
            si7021 = SI7021(i2c)

            rtc = machine.RTC()

            gcp_access_token = self._refresh_gcp_access_token()

            while True:
                refresh_access_token_bool = self.collect_weather_and_post_to_pubsub(
                    si7021=si7021,
                    rtc=rtc,
                    access_token=gcp_access_token,
                )

                if refresh_access_token_bool:
                    gcp_access_token = self._refresh_gcp_access_token()
                else:
                    led.off()
                    sleep(30)
                    led.on()
        finally:
            led.off()

    def connect_to_wifi(self):
        wlan = network.WLAN(network.STA_IF)

        wlan.active(True)

        wlan.connect(self.WIFI_NAME, self.WIFI_PASSWORD)

        sleep(20)

        if wlan.isconnected():
            print("WiFi Successfully Connected")
        else:
            raise Exception("Not able to connect")

    def collect_weather_and_post_to_pubsub(
        self,
        si7021: SI7021,
        rtc: machine.RTC,
        access_token: str,
    ) -> bool:
        datetime_now = self._get_datetime_formatted(timestamp=rtc.datetime())

        humidity = si7021.humidity()
        temperature_celsius = si7021.temperature()
        temperature_fahrenheit = (temperature_celsius * 9 / 5) + 32

        messages = bytes(
            ",".join(
                [
                    str(datetime_now),
                    str(temperature_fahrenheit),
                    str(humidity),
                    str(self.RASPBERRY_PI_PICO_W_ID),
                ]
            ),
            "utf-8",
        )

        return self.publish_pubsub_message_to_topic(
            access_token=access_token,
            messages=messages,
        )

    def _get_datetime_formatted(self, timestamp: str) -> str:
        """
        rtc = machine.RTC()
        timestamp=rtc.datetime()
        """
        return "%04d-%02d-%02d %02d:%02d:%02d" % (timestamp[0:3] + timestamp[4:7])

    def publish_pubsub_message_to_topic(
        self,
        access_token: str,
        messages: bytes,
    ) -> bool:
        for idx in range(5):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            raw_data = {
                "messages": [
                    {
                        "data": b64encode(messages),
                    },
                ],
            }

            response = requests.post(
                self.GCP_PUBSUB_PUBLISH_URL,
                data=json.dumps(raw_data),
                headers=headers,
            )

            status_code = response.status_code

            response.close()

            if status_code == 403 or status_code == 401:
                return True
            elif status_code == 200:
                return False
            else:
                sleep(2**idx)
        else:
            raise Exception("Failed Exponential Backoff")

    def _refresh_gcp_access_token(self) -> str:
        """Refreshes GCP Access Token with Refresh Token constant

        :returns: refresh token
        :rtype: str
        """
        params = f"client_id={self.GCP_CLIENT_ID}&client_secret={self.GCP_CLIENT_SECRET}&refresh_token={self.GCP_REFRESH_TOKEN}&grant_type=refresh_token"

        url = f"https://oauth2.googleapis.com/token?{params}"
        headers = {
            "Content-Type": "application/x-www-form-encoded",
            "Content-Length": "0",
        }

        response = requests.post(
            url,
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception(f"{response.status_code} ->\n{response.text}")

        try:
            access_token = response.json()["access_token"]

            response.close()

            return access_token
        except KeyError:
            raise Exception("No access_token key ->\n{response.json()}")


if __name__ == "__main__":
    SkyPiStreamer().stream()
