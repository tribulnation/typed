"""Connection-level error frames: the login a connection lost, and the reset it announced.

Bitget answers a private subscribe on a connection it holds no login for with `30004`
("User not logged in"), and announces a reset with an unsolicited `30033` ("Service upgrade
in progress. Connection reset imminent. Please reconnect."). After such an upgrade the same
connection (same `connId`) kept answering `30004` for an hour: a login is bound to one
physical connection, so the cure is a fresh one, logged in anew.

`BaseSocketConnection` records the connection its login was made on (`logged_in`). A
connection that announces a reset, or reports a lost login unprompted, is closed: its
streams raise `NetworkError`, and the next subscribe opens, and logs in to, a fresh one. A
private subscribe refused with `30004` reconnects the same way and retries, with backoff.
"""

from typing_extensions import Any, Mapping
from datetime import timedelta

from typed_core.exceptions import BadRequest

LOGIN_REQUIRED = '30004'
"""A private request on a connection the server holds no login for."""
SERVICE_UPGRADE = '30033'
"""The server is about to reset the connection and asks the client to reconnect."""
LOGIN_ATTEMPTS = 4
"""Private subscribes tried, each on a fresh logged-in connection, before `30004` is raised."""
LOGIN_BACKOFF = timedelta(seconds=0.5)
"""Pause before the second attempt, doubled before each later one."""


def error_code(frame: Mapping[str, Any]) -> str | None:
  """An error frame's `code`, as a string (Bitget sends it either way)."""
  if (code := frame.get('code')) is not None:
    return str(code)


def login_required(exc: BadRequest) -> bool:
  """Whether a refused request failed for want of a login on its connection."""
  reply = exc.args[0] if exc.args else None
  return isinstance(reply, Mapping) and error_code(reply) == LOGIN_REQUIRED


def resets_connection(frame: Mapping[str, Any], *, awaiting_ack: bool) -> bool:
  """Whether an error frame condemns its connection: a reset notice, or a lost login
  reported while no request awaits an ack (so it answers nothing the caller sent)."""
  code = error_code(frame)
  return code == SERVICE_UPGRADE or (code == LOGIN_REQUIRED and not awaiting_ack)


def backoff(attempt: int) -> float:
  """Seconds to wait before retry `attempt` (1-based)."""
  return LOGIN_BACKOFF.total_seconds() * 2 ** (attempt - 1)
