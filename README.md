# Hilton Hotel Booking Assistant

Streamlit frontend the Hilton booking assistant app. This keeps the transcript in the current Streamlit session, and displays the agent’s replies. Starting a new chat clears the transcript. Reloading the browser page also starts a fresh session.

## How to Run

Use Python 3.11 or later. Run these commands from the extracted project folder. The AWS endpoint is configured in `.streamlit/secrets.toml`.


**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**macOS or Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Set the `HILTON_CHAT_API_URL` environment variable to override the endpoint. If the endpoint is missing or the request fails, there will be an error in chat.

## API

The client sends the new user message and the history returned by the previous successful request.

The app displays the `reply` string and saves the returned `history` list for the next call. Starting a new chat clears both the transcript and the API history.
