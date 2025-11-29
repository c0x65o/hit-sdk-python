# Hit SDK - Python

Strongly-typed Python client libraries for Hit platform microservices.

## Installation

### Production (Git-based)

Add to your `pyproject.toml`:

```toml
[tool.uv.sources]
hit-sdk = { git = "https://github.com/c0x65o/hit-sdk-python.git" }
```

Or pin to a specific version:

```toml
[tool.uv.sources]
hit-sdk = { git = "https://github.com/c0x65o/hit-sdk-python.git", tag = "v1.0.0" }
```

### Local Development (Editable Mode)

For local development with editable mode:

```bash
uv source hit-sdk --path ../../hit-sdk-python
```

Or manually edit `pyproject.toml`:

```toml
[tool.uv.sources]
hit-sdk = { path = "../../hit-sdk-python", editable = true }
```

## Versioning

This SDK uses semantic versioning. Check available versions:

```bash
git ls-remote --tags https://github.com/c0x65o/hit-sdk-python.git
```

Pin to a specific version using tags:

```toml
[tool.uv.sources]
hit-sdk = { git = "https://github.com/c0x65o/hit-sdk-python.git", tag = "v1.0.0" }
```

Or pin to a specific commit SHA:

```toml
[tool.uv.sources]
hit-sdk = { git = "https://github.com/c0x65o/hit-sdk-python.git", rev = "abc123def456..." }
```

## Usage

```python
from hit import Client, Config

config = Config(api_url="https://api.example.com")
client = Client(config)

# Use client methods
response = await client.ping_pong.ping()
```

## Updating

To update to the latest version:

```bash
uv lock --upgrade-package hit-sdk
```

Or use the Hit CLI:

```bash
hit sdk update
```

