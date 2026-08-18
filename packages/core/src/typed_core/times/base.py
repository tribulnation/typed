from typing_extensions import TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime

T = TypeVar('T')

class TimeConverter(ABC, Generic[T]):
  """Abstract base class for time conversion between wire format and `datetime`."""

  @abstractmethod
  def parse(self, value: T) -> datetime:
    ...

  @abstractmethod
  def dump(self, dt: datetime) -> T:
    ...

  @abstractmethod
  def now(self) -> T:
    ...