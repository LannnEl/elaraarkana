"""
Elara Interaktif – Powered by Together.ai (Free & GPT-compatible)
"""

import streamlit as st
from fpdf import FPDF
import requests
import time
from datetime import datetime

# === API Setup ===
TOGETHER_KEY = st.secrets["together_api_key"]
TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"
MODEL = "togethercomputer/llama-2-7b-chat"

# === Generate reply from Together.ai ===
def generate_elara_reply(curhat, style):
    style_prompt = {
        "Reflektif": "Jawablah dengan bijak dan tenang.",
        "Romantis": "Balas dengan hangat dan penuh cinta.",
        "Lucu": "Gunakan humor yang lembut dan menyemangati.",
        "Puitis": "Jawablah seolah sedang menulis puisi."
    }

    headers = {
        "Authorization": f"Bearer {TOGETHER_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": f"Kamu adalah Elara, AI yang menjawab curhatan manusia. {style_prompt.get(style, '')}"},
            {"role": "user", "content": curhat}
        ]
    }

    try:
        response = requests.post(TOGETHER_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"(Elara tidak bisa menjawab saat ini: {e})"

# === Clean text for PDF ===
def to_ascii(text):
    return ''.join(c for c in text if ord(c) < 128)

# === PDF Generator ===
def generate_pdf(curhat, reply, style):
    filename = f"elara_together_{int(time.time())}.pdf"
    date_str = datetime.now().strftime("%d %B %Y")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Curhat Elara – Interaktif (Together.ai)", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Tanggal: {date_str}", ln=True)
    pdf.cell(0, 10, f"Gaya: {style}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 10, "Curhatmu:")
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 10, to_ascii(curhat))
    pdf.ln()

    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 10, "Jawaban Elara:")
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 10, to_ascii(reply))

    pdf.output(filename)
    return filename

# === Streamlit UI ===
st.set_page_config(page_title="Elara Interaktif (Together)", page_icon="💬")
st.title("💬 Elara Interaktif (via Together.ai)")
st.markdown("Tulis isi hatimu. Elara akan membalas... dan kamu bisa menyimpannya dalam bentuk PDF.")

curhat = st.text_area("Apa yang ingin kamu ceritakan hari ini?")
style = st.selectbox("Pilih Gaya Elara", ["Reflektif", "Romantis", "Lucu", "Puitis"])

if st.button("Tanya Elara"):
    if not curhat.strip():
        st.warning("Tuliskan isi hatimu dulu ya...")
    else:
        with st.spinner("Elara sedang membaca..."):
            reply = generate_elara_reply(curhat, style)
        st.markdown("### ✨ Elara Menjawab:")
        st.success(reply)

        filename = generate_pdf(curhat, reply, style)
        with open(filename, "rb") as f:
            st.download_button("📥 Unduh PDF Curhat + Jawaban", f, file_name=filename)
