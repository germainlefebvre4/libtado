# -*- coding: utf-8 -*-

"""Exceptions raised by libtado.

`TadoError` is the common base of every error the library raises on its own
behalf. `TadoHTTPError` additionally derives from
`requests.exceptions.HTTPError`, so code written as
`except requests.exceptions.HTTPError` keeps working.
"""

import requests


class TadoError(Exception):
  """Base class of all libtado errors."""


class TadoAuthError(TadoError):
  """Problem in the OAuth2 device-code login flow (started twice, not started, code expired)."""


class TadoHTTPError(TadoError, requests.exceptions.HTTPError):
  """A Tado host answered with a non-success HTTP status.

  Attributes:
    status_code (int): The HTTP status code, or `None` if there is no response.
    response (requests.Response): The response that caused the error.
  """

  def __init__(self, message: str = None, response: requests.Response = None, request=None):
    requests.exceptions.HTTPError.__init__(self, message, response=response, request=request)

  @property
  def status_code(self):
    return self.response.status_code if self.response is not None else None


class TadoRateLimitError(TadoHTTPError):
  """The API answered HTTP 429 and the retry policy did not resolve it.

  Attributes:
    retry_after (float): Seconds the server asked to wait, or `None` if unknown.
  """

  def __init__(self, message: str = None, response: requests.Response = None, request=None, retry_after: float = None):
    super().__init__(message, response=response, request=request)
    self.retry_after = retry_after


def error_from_response(response: requests.Response, retry_after: float = None):
  """Map a non-success `Response` to the matching exception, or return `None` if it succeeded."""
  if response.status_code < 400:
    return None
  reason = response.reason or ""
  message = f"{response.status_code} Error: {reason} for url: {response.url}"
  if response.status_code == 429:
    return TadoRateLimitError(message, response=response, retry_after=retry_after)
  return TadoHTTPError(message, response=response)
