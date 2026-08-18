from typing_extensions import Any
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator

validate_response = validator(dict[str, Any])


class Get(RpcEndpoint):
  async def __call__(self, *, validate: bool | None = None) -> dict[str, Any]:
    """Using the token you received from our backend, inject it into our embed by queryParam.

    <div class="box-info-wrapper">
      <div class="box-info-title">
        <i class="material-symbols-outlined">info</i>
        <h6>Production</h6>
      </div>
      <br>
      <h6 class="embed-link">
        https://embed.bit2me.com/dashboard?t=token&lang=language
      </h6>
    </div>
    <br> Queryparams supported:
    <div class="box-info-wrapper">
      <p class="queryparam-info"><strong>t</strong>: the obtained token from step 3. (MANDATORY).</p>
      <p class="queryparam-info"><strong>lang</strong>: the language to be loaded. Must be one of ['en','es','pt']. Defaults to 'en' (OPTIONAL).</p>
    </div>

    Args:
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/auth-flow/GET/v1/account)
    """
    return await self.request(
      'GET',
      '/v1/account',
      validator=validate_response,
      validate=validate,
    )
