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

        for idx, row in df.iterrows():

            payload = {
                FIELD_MAP["Nama"]: str(row.get("Nama", "")),
                FIELD_MAP["ID TICKET"]: str(row.get("ID TICKET", "")),
                FIELD_MAP["SBU"]: str(row.get("SBU", "")),
                FIELD_MAP["Eskalasi Back Office"]: str(row.get("Eskalasi Back Office", "")),
                FIELD_MAP["Hasil Eskalasi"]: str(row.get("Hasil Eskalasi", ""))
            }

            # ======================
            # PICK UP TIME
            # ======================
            try:
                pickup = pd.to_datetime(
                    str(row.get("Pick Up Time"))
                )

                payload["entry.1083825887_hour"] = f"{pickup.hour:02d}"
                payload["entry.1083825887_minute"] = f"{pickup.minute:02d}"
                payload["entry.1083825887_second"] = f"{pickup.second:02d}"

            except Exception:
                payload["entry.1083825887_hour"] = "00"
                payload["entry.1083825887_minute"] = "00"
                payload["entry.1083825887_second"] = "00"

            # ======================
            # CREATE TICKET DATE
            # ======================
            try:
                tanggal = pd.to_datetime(
                    row.get("Create Ticket Date")
                )

                payload["entry.405968346_day"] = str(tanggal.day)
                payload["entry.405968346_month"] = str(tanggal.month)
                payload["entry.405968346_year"] = str(tanggal.year)

            except Exception:
                pass

            # ======================
            # CREATE TICKET TIME
            # ======================
            try:
                ctt = pd.to_datetime(
                    str(row.get("Create Ticket Time"))
                )

                payload["entry.1785211983_hour"] = f"{ctt.hour:02d}"
                payload["entry.1785211983_minute"] = f"{ctt.minute:02d}"
                payload["entry.1785211983_second"] = f"{ctt.second:02d}"

            except Exception:
                payload["entry.1785211983_hour"] = "00"
                payload["entry.1785211983_minute"] = "00"
                payload["entry.1785211983_second"] = "00"

            try:

                r = requests.post(
                    FORM_URL,
                    data=payload,
                    timeout=20,
                    allow_redirects=False
                )

                if r.status_code in [200, 302]:
                    sukses += 1
                else:
                    st.write(
                        f"Baris {idx+1} gagal: {r.status_code}"
                    )

            except Exception as e:
                st.write(
                    f"Baris {idx+1} error: {e}"
                )

            progress.progress(
                (idx + 1) / len(df)
            )

        st.success(
            f"Selesai. Berhasil memproses {sukses} data."
        )
