
import streamlit as st
import pandas as pd
import requests

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdJzVCp0QswGlQN_eWWT8zCbUq4tHcv4u9RfYEpjWE54vst1g/formResponse"

FIELD_MAP = {
    "Nama": "entry.1778972854",
    "ID TICKET": "entry.1131610637",
    "SBU": "entry.1847893431",
    "Eskalasi Back Office": "entry.2054975984",
    "Hasil Eskalasi": "entry.1035810770"
}

st.title("Excel ➜ Google Form Importer")

file = st.file_uploader("Upload Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    st.dataframe(df.head())
    st.write(f"Total data: {len(df)}")

    if st.button("Kirim ke Google Form"):
        progress = st.progress(0)
        sukses = 0

        for idx, (_, row) in enumerate(df.iterrows()):
            payload = {
    FIELD_MAP["Nama"]: row.get("Nama",""),
    FIELD_MAP["ID TICKET"]: row.get("ID TICKET",""),
    FIELD_MAP["SBU"]: row.get("SBU",""),
    FIELD_MAP["Eskalasi Back Office"]: row.get("Eskalasi Back Office",""),
    FIELD_MAP["Hasil Eskalasi"]: row.get("Hasil Eskalasi","")
}
            try:
                r = requests.post(FORM_URL, data=payload, timeout=20)

                if r.status_code == 200:
                sukses += 1
                else:
                st.write("Gagal:", r.status_code)

            except:
                pass

            progress.progress((idx + 1) / len(df))

        st.success(f"Selesai. Berhasil memproses {sukses} data.")
