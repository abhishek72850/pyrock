import urllib.request
import json
import traceback
from .exceptions import InvalidAPIStatus
from .logger import Logger


logger = Logger(__name__)


def handle_exceptions(exception=Exception, msg="Some error occured"):
    """A decorator for handling exceptions."""

    def wrapper(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception:
                logger.warning(msg)
                logger.debug(traceback.format_exc())
                return None

        return inner

    return wrapper



class Network:
    """A class for making network calls."""
    @staticmethod
    def _prepare_request(url, **kwargs):
        default_headers = {
            'content-type': 'application/json'
        }
        if "headers" in kwargs:
            kwargs["headers"].update(default_headers)
        else:
            kwargs["headers"] = default_headers

        return urllib.request.Request(url, **kwargs)

    @staticmethod
    def _make_request(url, **kwargs):
        response = urllib.request.urlopen(
            Network._prepare_request(url, **kwargs)
        )
        if response.status != 200:
            raise InvalidAPIStatus(f"API call returned with status {response.status}")
        return response

    @staticmethod
    @handle_exceptions(msg="Unable to parse response")
    def _parse_response(response):
        response_text = response.read().decode("utf-8")
        logger.debug(f"{response_text}")
        return json.loads(response_text)


    @staticmethod
    @handle_exceptions(msg="Unable to make get request")
    def get(url, **kwargs):
        """Makes a GET request to the given URL."""
        response = Network._make_request(url, **kwargs)
        return Network._parse_response(response)


    @staticmethod
    @handle_exceptions(msg="Unable to make post request")
    def post(url, data, **kwargs):
        """Makes a POST request to the given URL with the given data."""
        data = urllib.parse.urlencode(data)
        data = data.encode("utf-8")

        response = Network._make_request(url, data=data, **kwargs)
        return Network._parse_response(response)
