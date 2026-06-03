import streamlit as st
import pandas as pd
import requests

# GANTI DENGAN URL FORMRESPONSE FORM BARU
FORM_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdYY2hbRlhrCY_a06uH0keEsBBu8x6P3AzpZ2BmcmVERjaxpQ/formResponse"

st.title("Excel ➜ Google Form Importer")

file = st.file_uploader(
    "Upload Excel",
    type=["xlsx"]
)

if file:

    df = pd.read_excel(file)

    st.dataframe(df.head())

    st.write(
        f"Total data: {len(df)}"
    )

    if st.button("Kirim ke Google Form"):

        progress = st.progress(0)

        sukses = 0

        session = requests.Session()

        for idx, row in df.iterrows():

            payload = {}

            # Nama
            payload["entry.154565194"] = str(
                row.get("Nama", "")
            ).strip()

            # SBU
            payload["entry.1778899713"] = str(
                row.get("SBU", "")
            ).strip()

            # ID Ticket
            payload["entry.1082086380"] = str(
                row.get("ID TICKET", "")
            ).strip()

            # Eskalasi Back Office
            payload["entry.822984039"] = str(
                row.get(
                    "Eskalasi Back Office",
                    ""
                )
            ).strip()

            # Hasil Eskalasi
            payload["entry.49503729"] = str(
                row.get(
                    "Hasil Eskalasi",
                    ""
                )
            ).strip()

            # Keterangan Tambahan
            if "Keterangan Tambahan" in df.columns:

                ket = str(
                    row.get(
                        "Keterangan Tambahan",
                        ""
                    )
                ).strip()

                if ket and ket.lower() != "nan":

                    payload[
                        "entry.546067612"
                    ] = ket

            # Pick Up Time
            try:

                pickup = str(
                    row.get(
                        "Pick Up Time",
                        ""
                    )
                ).strip()

                if pickup:

                    h, m, s = pickup.split(":")

                    payload[
                        "entry.141665543_hour"
                    ] = h

                    payload[
                        "entry.141665543_minute"
                    ] = m

                    payload[
                        "entry.141665543_second"
                    ] = s

            except:
                pass

            # Create Ticket Date
            try:

                tanggal = pd.to_datetime(
                    row.get(
                        "Create Ticket Date"
                    )
                )

                payload[
                    "entry.1418866853_day"
                ] = str(tanggal.day)

                payload[
                    "entry.1418866853_month"
                ] = str(tanggal.month)

                payload[
                    "entry.1418866853_year"
                ] = str(tanggal.year)

            except:
                pass

            # Create Ticket Time
            try:

                jam = str(
                    row.get(
                        "Create Ticket Time",
                        ""
                    )
                ).strip()

                if jam:

                    h, m, s = jam.split(":")

                    payload[
                        "entry.2062984122_hour"
                    ] = h

                    payload[
                        "entry.2062984122_minute"
                    ] = m

                    payload[
                        "entry.2062984122_second"
                    ] = s

            except:
                pass

            try:

                response = session.post(
                    FORM_URL,
                    data=payload,
                    headers={
                        "User-Agent": "Mozilla/5.0"
                    },
                    timeout=30
                )

                # Google Form sering tetap sukses walaupun return HTML
                sukses += 1

            except Exception as e:

                st.error(
                    f"Baris {idx+1} error: {e}"
                )

                break

            progress.progress(
                (idx + 1) / len(df)
            )

        st.success(
            f"Selesai. Berhasil memproses {sukses} dari {len(df)} data."
        )
