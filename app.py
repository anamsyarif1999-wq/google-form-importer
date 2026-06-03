import streamlit as st
import pandas as pd
import requests

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdJzVCp0QswGlQN_eWWT8zCbUq4tHcv4u9RfYEpjWE54vst1g/formResponse"

st.title("Excel ➜ Google Form Importer")

file = st.file_uploader("Upload Excel", type=["xlsx"])

if file:

    df = pd.read_excel(file)

    st.dataframe(df.head())
    st.write(f"Total data: {len(df)}")

    if st.button("Kirim ke Google Form"):

        progress = st.progress(0)
        sukses = 0

        for idx, row in df.iterrows():

            payload = {}

            progress.progress((idx + 1) / len(df))

        st.success(
            f"Selesai. Berhasil memproses {sukses} data."
        )
