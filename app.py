import os

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from booking_api import BookingAPIError, CHECK_RESERVATION, request_reply

API_SETTING = "HILTON_CHAT_API_URL"
ASSISTANT_AVATAR = ":material/room_service:"
EXAMPLES = (
    ("Which Hilton brands include breakfast?", ":material/restaurant:"),
    ("Check room availability for December 26, 2026", ":material/calendar_month:"),
)


def get_endpoint() -> str:
    url = os.environ.get(API_SETTING, "").strip()
    if url:
        return url

    try:
        return str(st.secrets.get(API_SETTING, "")).strip()
    except StreamlitSecretNotFoundError:
        return ""


def clear_chat() -> None:
    chat.turns = []
    chat.api_history = []
    chat.pending_prompt = None


def queue_prompt(msg: str) -> None:
    chat.pending_prompt = msg.strip() or None


def queue_chat_input() -> None:
    queue_prompt(chat.chat_input)

def render_turn(turn: dict[str, str | None]) -> None:
    st.chat_message("user").text(turn["prompt"])
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        reply = turn["reply"]
        if reply is not None:
            st.markdown(reply)
        else:
            st.error(turn["error"] or f"The request was interrupted. {CHECK_RESERVATION}")


st.set_page_config(page_title="Hilton Hotel Booking Assistant", page_icon="🏨")
st.html(
    """
    <style>
        [data-testid="stMainBlockContainer"] {
            max-width: 56rem;
            padding-top: clamp(2rem, 7vh, 4rem);
            padding-bottom: 1rem;
        }

        .st-key-chat_header {
            padding-bottom: 1rem;
            border-bottom: 1px solid #dbe3ed;
        }
        .st-key-chat_header h1 {
            padding: 0;
            font-size: clamp(1.85rem, 4.6vw, 2.5rem);
            line-height: 1.1;
            letter-spacing: -0.045em;
        }
        .st-key-chat_header [data-testid="stCaptionContainer"] p {
            font-size: 1rem;
        }

        .st-key-starter_prompts {
            padding-top: 0.6rem;
        }
        .st-key-transcript {
            height: clamp(12rem, calc(100dvh - 20rem), 44rem) !important;
        }
        [data-testid="stChatMessage"] {
            padding: 1rem;
            border: 1px solid #e0e7ef;
            border-radius: 0.9rem;
            background: #ffffff;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            background: #eef4fb;
        }
    </style>
    """
)

url = get_endpoint()
chat = st.session_state
turns = chat.setdefault("turns", [])
#keep AWS tools separate from the chat bubbles
history = chat.setdefault("api_history", [])
msg = chat.setdefault("pending_prompt", None)

with st.container(key="chat_header"):
    
    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
        st.title("Hilton Hotel Booking Assistant", anchor=False, width="content")
        st.button(
            "New chat",
            icon=":material/add:",
            on_click=clear_chat,
            disabled=not turns or msg is not None,
        )
    st.caption("Ask about Hilton brands, check availability, or manage a demo reservation.")

if not turns and msg is None:
    with st.container(key="starter_prompts"):
        st.markdown("**Try a question**")
        with st.container(horizontal=True):
            for example, icon in EXAMPLES:
                st.button(example, icon=icon, on_click=queue_prompt, args=(example,))

st.chat_input(
    "Message the booking assistant",
    key="chat_input",
    on_submit=queue_chat_input,
    disabled=msg is not None,
)

if turns or msg is not None:
    with st.container(height=360, border=False, autoscroll=True, key="transcript"):
        for turn in turns:
            render_turn(turn)

        if msg is not None:
            # Clear queued message before sending it to prevent rerun
            chat.pending_prompt = None
            turn = {"prompt": msg, "reply": None, "error": None}
            turns.append(turn)

            st.chat_message("user").text(msg)
            with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
                if not url:
                    #Error message if endpoint not set, set in secrets.toml
                    turn["error"] = (
                        f"The booking service endpoint is missing. Set `{API_SETTING}` and restart the app."
                    )
                else:
                    try:
                        with st.spinner("Waiting for the booking service…"):
                            #Save history to sent with next call
                            reply, next_history = request_reply(url, msg, history)
                        turn["reply"] = reply
                        chat.api_history = next_history
                    except BookingAPIError as err:
                        turn["error"] = str(err)
            st.rerun()
