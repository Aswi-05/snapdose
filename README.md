# 💊 SnapDose

**Snap the strip. Know the dose.**

SnapDose is an AI chatbot that reads a photo of a medicine strip, box, or prescription and explains what is printed on it in plain language (English, Telugu, Hindi, or Tamil). It helps elders and caregivers who struggle with tiny, confusing medicine labels. A user chats with it, then sends a clear medicine summary to a family member's WhatsApp with one click.

> ⚠️ SnapDose is a **reading aid, not a doctor**. It only explains what is printed on the medicine. It never diagnoses, recommends medicines, or changes a dose. Always confirm with a doctor or pharmacist.

**Live link:** https://snapdose-dsrubcih7qygflzvq6sgsc.streamlit.app/

## Features

- Upload a photo of a medicine strip, box, or prescription, or type a question
- Plain-language explanation: name, strength, general use, timing, warnings, expiry
- Replies in English, Telugu, Hindi, or Tamil
- Follow-up chat (for example: "when should she take it?")
- One button sends the full medicine summary to a family member's WhatsApp
- Safety rules: reads only printed text, says when it is unsure, asks for a retake on blurry photos, refuses to diagnose

## Tech stack

- **Streamlit** for the chat interface
- **Google Gemini** (`gemini-3.5-flash`) for chat and vision
- **Twilio WhatsApp API** for sending the summary

## Project structure

```
snapdose/
├── app.py                      # the app itself
├── prompts.py                  # the AI's personality and safety rules
├── requirements.txt            # dependencies
├── .gitignore                  # keeps secrets.toml out of GitHub
└── .streamlit/
    └── secrets.toml.example    # template for your keys
```

## Prerequisites

- Python 3.9 or newer
- A free [Google AI Studio](https://aistudio.google.com) account (Gemini API key)
- A free [Twilio](https://www.twilio.com/try-twilio) account (WhatsApp sandbox)

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/YOUR-USERNAME/snapdose.git
   cd snapdose
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS / Linux
   venv\Scripts\activate.bat       # Windows (cmd)
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get your keys**
   - Gemini: aistudio.google.com → Get API key
   - Twilio: copy your Account SID and Auth Token from the Console
   - Twilio WhatsApp sandbox: Messaging → Try it out → Send a WhatsApp message. From the family member's WhatsApp, send the join code (for example `join happy-tiger`) to the sandbox number. This expires after about 72 hours of inactivity.
   - Twilio Content Template: Messaging → Content Template Builder → create a Text template with two variables and note its Content SID (starts with `HX`):
     ```
     Hi! SnapDose here. Medicine summary for {{1}}:

     {{2}}

     Sent with SnapDose. Please confirm everything with a doctor or pharmacist.
     ```

5. **Add your secrets**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   Open `.streamlit/secrets.toml` and fill in:
   ```toml
   GEMINI_API_KEY = "..."
   TWILIO_ACCOUNT_SID = "..."
   TWILIO_AUTH_TOKEN = "..."
   TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
   TWILIO_CONTENT_SID = "HX..."
   ```
   Never commit `secrets.toml`. It is already listed in `.gitignore`.

6. **Run the app**
   ```bash
   streamlit run app.py
   ```
   Open http://localhost:8501, enter your name, who the medicine is for, a language, and the family WhatsApp number (with country code), then upload a medicine photo.

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub (public).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, choose the repo, branch, and `app.py`.
4. Open **Settings → Secrets** and paste the contents of your local `secrets.toml`.
5. Deploy.

## Testing

Tested on real medicine strips and boxes, plus blurry photos, dark photos, non-medicine photos, and off-topic questions. _Add your results here, for example: "27 of 30 printed fields read correctly; all bad-photo cases handled safely."_

## Limitations

- It can misread damaged, blurry, or handwritten labels.
- It cannot replace a doctor or pharmacist.
- On the free Gemini tier, Google may use API data to improve its products. Use sample strips, not real patient records.
- The Twilio sandbox only sends to numbers that have joined it.

## Author

Aswija Sistu, GVPCEW
