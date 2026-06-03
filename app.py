import streamlit as st
import pandas as pd
import requests

FORM_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdYY2hbRIhrCY_a06uH0keEsBBu8x6P3AzpZ2BmcmVERjaxpQ/formResponse"

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

    if st.button(
        "Kirim ke Google Form"
    ):

        progress = st.progress(0)

        sukses = 0

        session = requests.Session()

        for idx, row in df.iterrows():

            payload = {}

            # ======================
            # NAMA
            # ======================
            payload["entry.154565194"] = str(
                row.get("Nama", "")
            ).strip()

            # ======================
            # SBU
            # ======================
            payload["entry.1778899713"] = str(
                row.get("SBU", "")
            ).strip()

            # ======================
            # ID TICKET
            # ======================
            payload["entry.1082086380"] = str(
                row.get("ID TICKET", "")
            ).strip()

            # ======================
            # ESKALASI BACK OFFICE
            # ======================
            payload["entry.822984039"] = str(
                row.get(
                    "Eskalasi Back Office",
                    ""
                )
            ).strip()

            # ======================
            # HASIL ESKALASI
            # ======================
            payload["entry.49503729"] = str(
                row.get(
                    "Hasil Eskalasi",
                    ""
                )
            ).strip()

            # ======================
            # KETERANGAN TAMBAHAN
            # ======================
            if (
                "Keterangan Tambahan"
                in df.columns
            ):

                ket = str(
                    row.get(
                        "Keterangan Tambahan",
                        ""
                    )
                ).strip()

                if (
                    ket
                    and ket.lower()
                    != "nan"
                ):

                    payload[
                        "entry.546067612"
                    ] = ket

            # ======================
            # PICK UP TIME
            # ======================
            try:

                pickup = str(
                    row.get(
                        "Pick Up Time",
                        ""
                    )
                ).strip()

                if pickup:

                    h, m, s = (
                        pickup.split(":")
                    )

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

            # ======================
            # CREATE TICKET DATE
            # ======================
            try:

                tanggal = pd.to_datetime(
                    row.get(
                        "Create Ticket Date"
                    )
                )

                payload[
                    "entry.1418866853_day"
                ] = str(
                    tanggal.day
                )

                payload[
                    "entry.1418866853_month"
                ] = str(
                    tanggal.month
                )

                payload[
                    "entry.1418866853_year"
                ] = str(
                    tanggal.year
                )

            except:
                pass

            # ======================
            # CREATE TICKET TIME
            # ======================
            try:

                jam = str(
                    row.get(
                        "Create Ticket Time",
                        ""
                    )
                ).strip()

                if jam:

                    h, m, s = (
                        jam.split(":")
                    )

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
                        "User-Agent":
                        "Mozilla/5.0",
                        "Referer":
                        "https://docs.google.com/forms/"
                    },
                    timeout=30,
                    allow_redirects=False
                )

                if response.status_code in [
                    200,
                    302
                ]:

                    sukses += 1

                else:

                    st.error(
                        f"Baris {idx+1} gagal ({response.status_code})"
                    )

                    st.write(
                        "Payload:"
                    )
                    st.json(
                        payload
                    )

                    st.write(
                        "Response:"
                    )
                    st.text(
                        response.text[:3000]
                    )

                    break

            except Exception as e:

                st.error(
                    f"Baris {idx+1} error: {e}"
                )

                break

            progress.progress(
                (idx + 1)
                / len(df)
            )

        st.success(
            f"Selesai. Berhasil memproses {sukses} dari {len(df)} data."
        )
