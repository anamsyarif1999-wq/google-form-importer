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

        session = requests.Session()

        for idx, row in df.iterrows():

            payload = {}

            # Nama
            payload["entry.1778972854"] = str(
                row.get("Nama", "")
            ).strip()

            # SBU
            payload["entry.1131610637"] = str(
                row.get("SBU", "")
            ).strip()

            # ID Ticket
            payload["entry.1847893431"] = str(
                row.get("ID TICKET", "")
            ).strip()

            # Eskalasi Back Office
            payload["entry.2054975984"] = str(
                row.get("Eskalasi Back Office", "")
            ).strip()

            # Hasil Eskalasi
            payload["entry.1035810770"] = str(
                row.get("Hasil Eskalasi", "")
            ).strip()

            # Keterangan Tambahan (opsional)
            if "Keterangan Tambahan" in df.columns:

                ket = str(
                    row.get("Keterangan Tambahan", "")
                ).strip()

                if ket and ket.lower() != "nan":
                    payload["entry.1789051105"] = ket

            # ==========================
            # Pick Up Time
            # ==========================
            try:

                pickup = str(
                    row.get("Pick Up Time", "")
                ).strip()

                if pickup:

                    h, m, s = pickup.split(":")

                    payload["entry.1083825887_hour"] = h
                    payload["entry.1083825887_minute"] = m
                    payload["entry.1083825887_second"] = s

            except Exception:
                pass

            # ==========================
            # Create Ticket Date
            # ==========================
            try:

                tanggal = pd.to_datetime(
                    row.get("Create Ticket Date")
                )

                payload["entry.405968346_day"] = str(
                    tanggal.day
                )

                payload["entry.405968346_month"] = str(
                    tanggal.month
                )

                payload["entry.405968346_year"] = str(
                    tanggal.year
                )

            except Exception:
                pass

            # ==========================
            # Create Ticket Time
            # ==========================
            try:

                jam = str(
                    row.get("Create Ticket Time", "")
                ).strip()

                if jam:

                    h, m, s = jam.split(":")

                    payload["entry.1785211983_hour"] = h
                    payload["entry.1785211983_minute"] = m
                    payload["entry.1785211983_second"] = s

            except Exception:
                pass

            try:

                response = session.post(
                    FORM_URL,
                    data=payload,
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Referer": "https://docs.google.com/forms/"
                    },
                    timeout=20,
                    allow_redirects=False
                )

                if response.status_code in [200, 302]:
                    sukses += 1

                else:

                    st.error(
                        f"Baris {idx+1} gagal: {response.status_code}"
                    )

                    st.write("Payload:")
                    st.json(payload)

                    st.write("Response:")
                    st.text(response.text[:2000])

                    break

            except Exception as e:

                st.error(
                    f"Baris {idx+1} error: {e}"
                )

                break

            progress.progress(
                (idx + 1) / len(df)
            )

        st.success(
            f"Selesai. Berhasil memproses {sukses} data."
        
