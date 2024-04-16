import requests
from urllib.parse import urlparse, parse_qs, urlunparse
import re
import codecs
import json



def check_email(email):
    # Initial URL
    url = "https://signup.live.com/signup"

    # Create a session
    with requests.Session() as s:
        # Make the first request
        response = s.get(url, allow_redirects=False)

        # If the response is a redirect
        if response.status_code == 302:
            # Get the redirect URL
            redirect_url = response.headers['Location']

            # Parse the redirect URL to extract the 'uaid' query parameter
            parsed_url = urlparse(redirect_url)
            uaid = parse_qs(parsed_url.query).get('uaid', [''])[0]

            # Create the first canary URL using the 'uaid'
            first_canary = f"https://signup.live.com/signup?lic=1&uaid={uaid}"

            # Make the second request to the first canary URL
            second_response = s.get(first_canary)

            # Use regex to find the 'apiCanary' value in the response
            match = re.search(r'"apiCanary":"(.*?)"', second_response.text)
            if match:
                # If 'apiCanary' is found, decode it
                api_canary_encoded = match.group(1)
                api_canary = codecs.decode(api_canary_encoded, 'unicode_escape')
            else:
                print("Could not find 'apiCanary' in the response")

            try:
                # Try to extract the 'amsc' cookie from the response
                amsc = second_response.cookies.get('amsc')

                # Create the headers for the next request
                headers = {
                    'cookie': f'amsc={amsc}',
                    'canary': api_canary,
                    'authority': 'signup.live.com',
                    'accept': 'application/json',
                    'content-type': 'application/json; charset=utf-8',
                    'origin': 'https://signup.live.com',
                } if amsc else {
                    'canary': api_canary,
                    'authority': 'signup.live.com',
                    'accept': 'application/json',
                    'content-type': 'application/json; charset=utf-8',
                    'origin': 'https://signup.live.com',
                }

            except Exception as e:
                # If an error occurs, print it
                print("Error:", e)

            # Define the data to be sent
            data = {
                "evts": [
                    {
                        "perf": {
                            "data": {
                                "navigation": {
                                    "type": 0,
                                    "redirectCount": 0
                                },
                            },
                        }
                    }
                ],
                "cm": {
                    "hst": "signup.live.com",
                    "av": None
                },
            }

            # Convert the data to a JSON string
            data_string = json.dumps(data)

            # Send the next request with the 'canary' value, 'amsc' header, and data
            ClientEvents = s.post("https://signup.live.com/API/ClientEvents", headers=headers, data=data_string)

            # Define the data to be sent in the next request
            json_data = {
                'pageApiId': 200639,
                'clientDetails': [],
                'userAction': '',
                'source': 'PageView',
                'clientTelemetryData': {
                    'category': 'PageLoad',
                    'pageName': '200639',
                    'eventInfo': {
                        'timestamp': 1712713102844,
                    },
                },
                'uiflvr': 1001,
            }

            # Convert the data to a JSON string
            data_string = json.dumps(json_data)

            ReportClientEvent = s.post("https://signup.live.com/API/ReportClientEvent", headers=headers, data=data_string)

            # Define the data to be sent in the next request
            json_data = {
                'signInName': email,
            }

            # Convert the data to a JSON string
            data_string = json.dumps(json_data)

            CheckAvailableSigninNames = s.post("https://signup.live.com/API/CheckAvailableSigninNames", headers=headers, data=data_string)

            # Convert the response text to a dictionary
            response_dict = json.loads(CheckAvailableSigninNames.text)

            return response_dict

