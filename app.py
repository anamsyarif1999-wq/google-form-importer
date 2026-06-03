import streamlit as st
import pandas as pd
import requests

FORM_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdJzVCp0QswGlQN_eWWT8zCbUq4tHcv4u9RfYEpjWE54vst1g/formResponse"

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

        for idx, row in df.iterrows():

            payload = {
                FIELD_MAP["Nama"]: row.get("Nama", ""),
                FIELD_MAP["ID TICKET"]: row.get("ID TICKET", ""),
                FIELD_MAP["SBU"]: row.get("SBU", ""),
                FIELD_MAP["Eskalasi Back Office"]: row.get("Eskalasi Back Office", ""),
                FIELD_MAP["Hasil Eskalasi"]: row.get("Hasil Eskalasi", "")
            }

            # Pick Up Time
            pickup = str(row.get("Pick Up Time", "00:00:00"))

            try:
                h, m, s = pickup.split(":")
            except:
                h, m, s = "00", "00", "00"

            payload["entry.1083825887_hour"] = h
            payload["entry.1083825887_minute"] = m
            payload["entry.1083825887_second"] = s

            # Create Ticket Date
            try:
                tanggal = pd.to_datetime(
                    row.get("Create Ticket Date")
                )

                payload["entry.405968346_day"] = str(tanggal.day)
                payload["entry.405968346_month"] = str(tanggal.month)
                payload["entry.405968346_year"] = str(tanggal.year)

            except:
                pass

            # Create Ticket Time
            ctt = str(row.get("Create Ticket Time", "00:00:00"))

            try:
                h2, m2, s2 = ctt.split(":")
            except:
                h2, m2, s2 = "00", "00", "00"

            payload["entry.1785211983_hour"] = h2
            payload["entry.1785211983_minute"] = m2
            payload["entry.1785211983_second"] = s2

            try:

                r = requests.post(
                    FORM_URL,
                    data=payload,
                    timeout=20
                )

                if r.status_code == 200:
                    sukses += 1
                else:
                    st.write(
                        f"Gagal: {r.status_code}"
                    )

            except Exception as e:
                st.write(e)

            progress.progress(
                (idx + 1) / len(df)
            )

        st.success(
            f"Selesai. Berhasil memproses {sukses} data."
        )
