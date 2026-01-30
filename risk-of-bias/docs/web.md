# Web Interface

A simple web front end is provided using [FastAPI](https://fastapi.tiangolo.com/).
It lets you upload a PDF and view the standard RoB2 HTML report directly in your
browser.

![Web Interface](web.jpeg)

## Running the server

Install the optional dependencies and start the server with `risk-of-bias web` (equivalent to `make web`):

```console
pip install "risk_of_bias[web]"
risk-of-bias web
```

Open `http://127.0.0.1:8000` and upload your manuscript. After processing you
will see the report along with links to download the JSON and Markdown
representations.

If the `OPENAI_API_KEY` environment variable is not set when the server
starts, the upload form will include a field to provide it. When supplied,
the key is used for that analysis session.

A standalone macOS application based on this interface is generated for each
release. It only processes one PDF at a time and can be downloaded from the
[latest release](https://github.com/rob-luke/risk-of-bias/releases/latest/download/RiskOfBias).

## Authentication

The web interface supports optional username/password authentication. When
enabled, users must sign in before accessing the upload form and downloading
results.

### Enabling authentication

Set both `WEB_USERNAME` and `WEB_PASSWORD` environment variables to enable
authentication:

```bash
export WEB_USERNAME=admin
export WEB_PASSWORD=your-secure-password
risk-of-bias web
```

Or add them to your `.env` file:

```ini
WEB_USERNAME=admin
WEB_PASSWORD=your-secure-password
```

### Configuration options

| Variable | Description | Required |
|----------|-------------|----------|
| `WEB_USERNAME` | Username for login | Yes (to enable auth) |
| `WEB_PASSWORD` | Password for login | Yes (to enable auth) |
| `WEB_SECRET_KEY` | Secret key for signing session tokens | No (auto-generated) |

!!! note
    When neither `WEB_USERNAME` nor `WEB_PASSWORD` is set, authentication is
    disabled and the web interface is accessible without login. This is the
    default behaviour for local development.

### Session management

Sessions are managed using signed HTTP-only cookies that expire after 24 hours.
Users can sign out by clicking the "Sign Out" link in the top right corner
of the upload form.
