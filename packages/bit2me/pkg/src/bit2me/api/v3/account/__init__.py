from .get import Get
from .identity_verification import IdentityVerification


class Account(Get, IdentityVerification): ...
