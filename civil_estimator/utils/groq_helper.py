"""
Thin wrapper around the Groq API for the AI Assistant tab.
Get a free API key from https://console.groq.com -> API Keys.
"""

import streamlit as st
from groq import Groq

SYSTEM_PROMPT = (
    "You are a helpful civil engineering assistant embedded in a construction "
    "quantity-takeoff app. Explain formulas, mix ratios, and calculation results "
    "clearly and briefly for engineering students and site engineers. "
    "Keep answers concise and practical."
)


def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        return None
    return Groq(api_key=api_key)


def ask_groq(user_question: str, context: str = "") -> str:
    client = get_groq_client()
    if client is None:
        return (
            "⚠️ Groq API key not found. Add GROQ_API_KEY in `.streamlit/secrets.toml` "
            "(local) or in your Streamlit Cloud app's Secrets settings."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.append({"role": "system", "content": f"Current calculation context:\n{context}"})
    messages.append({"role": "user", "content": user_question})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # check console.groq.com for current available models
            messages=messages,
            temperature=0.4,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Groq API error: {e}"
