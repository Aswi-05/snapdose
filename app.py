import json
import re

import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient

from prompts import (
    LANGUAGES,
    SUMMARY_REQUEST_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    get_system_prompt,
)

MODEL_NAME = 'gemini-3.5-flash'

st.set_page_config(page_title='SnapDose', page_icon='💊')

GEMINI_API_KEY = st.secrets['GEMINI_API_KEY']
TWILIO_ACCOUNT_SID = st.secrets['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = st.secrets['TWILIO_AUTH_TOKEN']
TWILIO_WHATSAPP_FROM = st.secrets['TWILIO_WHATSAPP_FROM']
TWILIO_CONTENT_SID = st.secrets['TWILIO_CONTENT_SID']


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


@st.cache_resource
def get_twilio_client():
    return TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


gemini_client = get_gemini_client()
twilio_client = get_twilio_client()


def render_message(message):
    with st.chat_message(message['role']):
        if message['kind'] == 'text':
            st.write(message['content'])
        elif message['kind'] == 'image':
            st.image(message['content'])


def add_message(role, kind, content):
    st.session_state.messages.append({'role': role, 'kind': kind, 'content': content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text or 'Sorry, I could not read that. Please try again.'
    except Exception as error:
        return f'Sorry, something went wrong: {error}'


def clean_whatsapp_text(text):
    if not text:
        return 'No medicine summary available.'
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = ' | '.join(lines)  # template variables cannot contain line breaks
    text = ' '.join(text.split())
    return text[:1500] + '...' if len(text) > 1500 else text


def send_whatsapp(to_number, patient, summary):
    # Content template expects {{1}} = patient name, {{2}} = summary.
    try:
        content_variables = json.dumps(
            {'1': patient, '2': clean_whatsapp_text(summary)}, ensure_ascii=False
        )
        message = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=f'whatsapp:{to_number}',
            content_sid=TWILIO_CONTENT_SID,
            content_variables=content_variables,
        )
        return True, message.sid
    except Exception as error:
        return False, str(error)


# Step 1: onboarding
if 'onboarded' not in st.session_state:
    st.title('💊 SnapDose')
    st.caption('Snap the strip. Know the dose.')

    with st.form('onboarding_form'):
        name = st.text_input('Your name')
        patient = st.text_input('Who is the medicine for?', placeholder='e.g. Ammamma')
        language = st.selectbox('Explain in', LANGUAGES)
        whatsapp_number = st.text_input(
            'Family WhatsApp number (with country code)',
            placeholder='+91XXXXXXXXXX',
            help='This is the number SnapDose will text the medicine summary to.',
        )
        submitted = st.form_submit_button('Let us go 💊')

    if submitted:
        number = whatsapp_number.replace(' ', '')
        if not name.strip() or not patient.strip():
            st.warning('Please fill in your name and who the medicine is for.')
        elif not re.fullmatch(r'\+\d{10,15}', number):
            st.warning('Enter the number with country code, like +919876543210.')
        else:
            st.session_state.name = name.strip()
            st.session_state.patient = patient.strip()
            st.session_state.language = language
            st.session_state.whatsapp_number = number
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=get_system_prompt(language, patient.strip())
                ),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()

# Step 2: chat interface
header_col, button_col = st.columns([5, 2], vertical_alignment='center')
with header_col:
    st.title('💊 SnapDose')
with button_col:
    send_disabled = len(st.session_state.messages) == 0
    if st.button('📲 Send to WhatsApp', disabled=send_disabled):
        with st.spinner('Preparing the medicine summary...'):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
            success, info = send_whatsapp(
                st.session_state.whatsapp_number, st.session_state.patient, summary
            )
        if success:
            st.success('Sent! Check the family WhatsApp 💊')
        else:
            st.error(f'Could not send that: {info}')

st.caption(
    f'Reading for {st.session_state.patient} - summary goes to '
    f'{st.session_state.whatsapp_number}. SnapDose is a reading aid, not medical advice.'
)

if not st.session_state.messages:
    add_message('assistant', 'text', WELCOME_MESSAGE_TEMPLATE.format(
        name=st.session_state.name,
        patient=st.session_state.patient,
        language=st.session_state.language,
    ))
else:
    for message in st.session_state.messages:
        render_message(message)

user_input = st.chat_input(
    'Ask a question, or attach a photo of the medicine strip',
    accept_file=True,
    file_type=['jpg', 'jpeg', 'png'],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message('user', 'image', photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message('user', 'text', text)
        parts.append(text)
    elif photo is not None:
        parts.append('Read this medicine photo and explain what is printed on it.')

    with st.spinner('Reading the label...'):
        answer = ask_gemini(parts)
    add_message('assistant', 'text', answer)