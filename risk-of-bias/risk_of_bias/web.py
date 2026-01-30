from __future__ import annotations

import hashlib
import hmac
import os
import tempfile
import time
import uuid
import webbrowser
from pathlib import Path
from typing import Optional

from fastapi import Cookie, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from risk_of_bias.config import settings
from risk_of_bias.frameworks.rob2 import get_rob2_framework
from risk_of_bias.run_framework import run_framework
from risk_of_bias.types._framework_types import Framework

APP_TEMP_DIR = Path(tempfile.gettempdir()) / "risk_of_bias_web"
APP_TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Session expiry time in seconds (24 hours)
SESSION_EXPIRY = 86400

app = FastAPI()


def _create_session_token(username: str) -> str:
    """Create a signed session token for a user.

    Parameters
    ----------
    username : str
        The username to create a session for.

    Returns
    -------
    str
        A signed session token containing username and expiry timestamp.
    """
    expiry = int(time.time()) + SESSION_EXPIRY
    data = f"{username}:{expiry}"
    signature = hmac.new(
        settings.web_secret_key.encode(),
        data.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{data}:{signature}"


def _verify_session_token(token: str) -> Optional[str]:
    """Verify a session token and return the username if valid.

    Parameters
    ----------
    token : str
        The session token to verify.

    Returns
    -------
    Optional[str]
        The username if the token is valid and not expired, None otherwise.
    """
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        username, expiry_str, signature = parts
        expiry = int(expiry_str)

        # Check if token has expired
        if time.time() > expiry:
            return None

        # Verify signature
        data = f"{username}:{expiry_str}"
        expected_signature = hmac.new(
            settings.web_secret_key.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()

        if hmac.compare_digest(signature, expected_signature):
            return username
        return None
    except (ValueError, AttributeError):
        return None


def _is_authenticated(session_token: Optional[str]) -> bool:
    """Check if the current request is authenticated.

    Parameters
    ----------
    session_token : Optional[str]
        The session token from the request cookie.

    Returns
    -------
    bool
        True if authentication is disabled or the session is valid.
    """
    if not settings.auth_enabled:
        return True
    if not session_token:
        return False
    return _verify_session_token(session_token) is not None


def _get_login_html() -> str:
    """Return the HTML for the login page.

    Returns
    -------
    str
        HTML content for the login form.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Risk of Bias Assessment</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 min-h-screen flex items-center justify-center">
        <div class="max-w-md w-full space-y-8 p-8">
            <div class="text-center">
                <h1 class="text-3xl font-bold text-gray-900 mb-2">Risk of Bias Assessment</h1>
                <p class="text-gray-600 mb-8">Please sign in to continue</p>
            </div>

            {{ERROR_MESSAGE}}

            <form action="/login" method="post" class="space-y-6">
                <div>
                    <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                        Username
                    </label>
                    <input type="text" id="username" name="username" required
                        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                </div>

                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                        Password
                    </label>
                    <input type="password" id="password" name="password" required
                        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                </div>

                <div>
                    <button type="submit" class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                        Sign In
                    </button>
                </div>
            </form>
        </div>
    </body>
    </html>
    """


@app.get("/login", response_class=HTMLResponse)
def login_page(error: Optional[str] = None) -> str:
    """Return the login page.

    Parameters
    ----------
    error : Optional[str]
        Optional error message to display.

    Returns
    -------
    str
        HTML content for the login page.
    """
    html = _get_login_html()
    if error:
        error_html = (
            '<div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">'
            '<div class="flex">'
            '<div class="ml-3">'
            '<p class="text-sm text-red-700">Invalid username or password</p>'
            "</div>"
            "</div>"
            "</div>"
        )
        return html.replace("{{ERROR_MESSAGE}}", error_html)
    return html.replace("{{ERROR_MESSAGE}}", "")


@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
) -> RedirectResponse:
    """Process login form submission.

    Parameters
    ----------
    username : str
        The submitted username.
    password : str
        The submitted password.

    Returns
    -------
    RedirectResponse
        Redirect to main page on success, or login page with error on failure.
    """
    if username == settings.web_username and password == settings.web_password:
        response = RedirectResponse(url="/", status_code=303)
        token = _create_session_token(username)
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            max_age=SESSION_EXPIRY,
            samesite="lax",
        )
        return response

    return RedirectResponse(url="/login?error=1", status_code=303)


@app.get("/logout")
def logout() -> RedirectResponse:
    """Log out the current user.

    Returns
    -------
    RedirectResponse
        Redirect to login page after clearing the session cookie.
    """
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session_token")
    return response


@app.get("/", response_class=HTMLResponse, response_model=None)
def index(
    session_token: Optional[str] = Cookie(None),
) -> HTMLResponse | RedirectResponse:
    """Return a simple upload form.

    Parameters
    ----------
    session_token : Optional[str]
        Session token from cookie for authentication.

    Returns
    -------
    HTMLResponse | RedirectResponse
        The upload form HTML, or redirect to login if authentication required.
    """
    if not _is_authenticated(session_token):
        return RedirectResponse(url="/login", status_code=303)

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Risk of Bias Assessment</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 min-h-screen flex items-center justify-center">
        {{LOGOUT_BUTTON}}
        <div class="max-w-md w-full space-y-8 p-8">
            <div class="text-center">
                <h1 class="text-3xl font-bold text-gray-900 mb-2">Risk of Bias Assessment</h1>
                <p class="text-gray-600 mb-8">Upload a PDF manuscript to analyze potential bias in research methodology</p>
            </div>
            
            <form id="uploadForm" action="/analyze" method="post" enctype="multipart/form-data" class="space-y-6">
                <div>
                    <label for="file" class="block text-sm font-medium text-gray-700 mb-2">
                        Select PDF Manuscript
                    </label>
                    <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
                        <div class="space-y-1 text-center">
                            <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                            <div class="flex text-sm text-gray-600">
                                <label for="file" class="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
                                    <span>Upload a file</span>
                                    <input id="file" name="file" type="file" accept="application/pdf" required class="sr-only">
                                </label>
                                <p class="pl-1">or drag and drop</p>
                            </div>
                            <p class="text-xs text-gray-500">PDF up to 10MB</p>
                        </div>
                    </div>
                </div>

                <div>
                    <label for="model" class="block text-sm font-medium text-gray-700 mb-2">
                        Select AI Model
                    </label>
                    <select id="model" name="model" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                        {{MODEL_OPTIONS}}
                    </select>
                </div>

                {{API_KEY_FIELD}}

                <div>
                    <button type="submit" class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                        Analyze Risk of Bias
                    </button>
                </div>
            </form>
            
            <!-- Loading state (hidden by default) -->
            <div id="loadingState" class="hidden text-center space-y-4">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <div>
                    <h3 class="text-lg font-medium text-gray-900">Processing your manuscript...</h3>
                    <p class="text-sm text-gray-600 mt-2">This may take several minutes. Please don't close this window.</p>
                </div>
            </div>
        </div>
        
        <script>
            const dropZone = document.querySelector('.border-dashed');
            const fileInput = document.getElementById('file');
            const fileLabel = document.querySelector('label[for="file"] span');
            
            // Form submission handler
            document.getElementById('uploadForm').addEventListener('submit', function() {
                // Hide the form and show loading state
                document.getElementById('uploadForm').style.display = 'none';
                document.getElementById('loadingState').classList.remove('hidden');
            });
            
            // Update file input display when file is selected
            fileInput.addEventListener('change', function(e) {
                const fileName = e.target.files[0]?.name;
                if (fileName) {
                    fileLabel.textContent = fileName;
                }
            });
            
            // Drag and drop handlers
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, preventDefaults, false);
                document.body.addEventListener(eventName, preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, unhighlight, false);
            });
            
            dropZone.addEventListener('drop', handleDrop, false);
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            function highlight(e) {
                dropZone.classList.add('border-indigo-400', 'bg-indigo-50');
            }
            
            function unhighlight(e) {
                dropZone.classList.remove('border-indigo-400', 'bg-indigo-50');
            }
            
            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                
                if (files.length > 0) {
                    const file = files[0];
                    if (file.type === 'application/pdf') {
                        fileInput.files = files;
                        fileLabel.textContent = file.name;
                    } else {
                        alert('Please select a PDF file.');
                    }
                }
            }
        </script>
    </body>
    </html>
    """

    options = (
        f'<option value="{settings.fast_ai_model}">{settings.fast_ai_model}</option>'
        f'<option value="{settings.good_ai_model}">{settings.good_ai_model}</option>'
        f'<option value="{settings.best_ai_model}">{settings.best_ai_model}</option>'
    )

    key_field = (
        "<div>"
        '<label for="api_key" class="block text-sm font-medium text-gray-700 mb-2">'
        "OpenAI API Key"
        "</label>"
        '<input type="text" id="api_key" name="api_key" '
        'class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" required>'
        "</div>"
    )

    if os.getenv("OPENAI_API_KEY"):
        html = html.replace("{{API_KEY_FIELD}}", "")
    else:
        html = html.replace("{{API_KEY_FIELD}}", key_field)

    # Add logout button if authentication is enabled
    if settings.auth_enabled:
        logout_button = (
            '<div class="absolute top-4 right-4">'
            '<a href="/logout" class="text-sm text-gray-600 hover:text-gray-900 '
            "bg-white px-3 py-2 rounded-md shadow-sm border border-gray-200 "
            'hover:bg-gray-50 transition-colors">Sign Out</a>'
            "</div>"
        )
        html = html.replace("{{LOGOUT_BUTTON}}", logout_button)
    else:
        html = html.replace("{{LOGOUT_BUTTON}}", "")

    return html.replace("{{MODEL_OPTIONS}}", options)


@app.post("/analyze", response_class=HTMLResponse, response_model=None)
def analyze(
    file: UploadFile = File(...),
    model: str = Form(settings.fast_ai_model),
    api_key: str | None = Form(None),
    session_token: Optional[str] = Cookie(None),
) -> str | RedirectResponse:
    """Process a PDF with the selected model and return the assessment HTML.

    Parameters
    ----------
    file : UploadFile
        The uploaded PDF file.
    model : str
        The AI model to use for analysis.
    api_key : str | None
        Optional OpenAI API key.
    session_token : Optional[str]
        Session token from cookie for authentication.

    Returns
    -------
    str | RedirectResponse
        The assessment HTML, or redirect to login if authentication required.
    """
    if not _is_authenticated(session_token):
        return RedirectResponse(url="/login", status_code=303)

    file_id = uuid.uuid4().hex
    work_dir = APP_TEMP_DIR / file_id
    work_dir.mkdir(parents=True, exist_ok=True)

    filename = file.filename or "manuscript.pdf"
    pdf_path = work_dir / filename
    with pdf_path.open("wb") as f:
        f.write(file.file.read())

    framework: Framework = run_framework(
        manuscript=pdf_path,
        framework=get_rob2_framework(),
        model=model,
        verbose=True,
        temperature=settings.temperature,
        api_key=api_key,
    )

    json_path = work_dir / "result.json"
    md_path = work_dir / "result.md"
    html_path = work_dir / "result.html"

    framework.save(json_path)
    framework.export_to_markdown(md_path)
    framework.export_to_html(html_path)

    html_content = html_path.read_text()
    download_links = (
        '<div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">'
        '<div class="flex">'
        '<div class="ml-3">'
        '<h3 class="text-sm font-medium text-blue-800">Download Results</h3>'
        '<div class="mt-2 text-sm text-blue-700">'
        '<p class="space-x-4">'
        f'<a href="/download/{file_id}/result.json" class="font-medium underline hover:text-blue-600">JSON </a> | '
        f'<a href="/download/{file_id}/result.md" class="font-medium underline hover:text-blue-600">Markdown </a> | '
        f'<a href="/download/{file_id}/result.html" class="font-medium underline hover:text-blue-600">HTML </a>'
        "</p>"
        "</div>"
        "</div>"
        "</div>"
        "</div>"
    )

    # Add Tailwind CSS to the results page if it doesn't already have it
    if '<script src="https://cdn.tailwindcss.com"></script>' not in html_content:
        html_content = html_content.replace(
            "<head>", '<head><script src="https://cdn.tailwindcss.com"></script>', 1
        )

    return html_content.replace("<body>", f"<body>{download_links}", 1)


@app.get("/download/{file_id}/{filename}", response_model=None)
def download(
    file_id: str,
    filename: str,
    session_token: Optional[str] = Cookie(None),
) -> FileResponse | RedirectResponse:
    """Return a saved file for download.

    Parameters
    ----------
    file_id : str
        The unique identifier for the analysis session.
    filename : str
        The name of the file to download.
    session_token : Optional[str]
        Session token from cookie for authentication.

    Returns
    -------
    FileResponse | RedirectResponse
        The requested file, or redirect to login if authentication required.
    """
    if not _is_authenticated(session_token):
        return RedirectResponse(url="/login", status_code=303)

    file_path = APP_TEMP_DIR / file_id / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)


# For local development
if __name__ == "__main__":
    import uvicorn

    webbrowser.open("http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
