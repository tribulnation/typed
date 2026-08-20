def path_join(*parts: str) -> str:
  return '/'.join([part.strip('/') for part in parts])
