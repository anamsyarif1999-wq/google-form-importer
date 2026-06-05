import streamlit as st
import pandas as pd
import requests
import json

FORM_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdYY2hbRIhrCY_a06uH0keEsBBu8x6P3AzpZ2BmcmVERjaxpQ/formResponse"

st.title("Excel ➜ Google Form Importer")

file = st.file_uploader(
    "Upload Excel",
    type=["xlsx"]
)

if file:

    df = pd.read_excel(file)

    st.dataframe(df.head())

    st.write(f"Total data: {len(df)}")

    if st.button("Kirim ke Google Form"):

        progress = st.progress(0)

        sukses = 0

        session = requests.Session()

        for idx, row in df.iterrows():

            try:

                payload = {}

                # ==================
                # TEXT FIELD
                # ==================

                payload["entry.154565194"] = str(
                    row.get("Nama", "")
                ).strip()

                payload["entry.1778899713"] = str(
                    row.get("SBU", "")
                ).strip()

                payload["entry.1082086380"] = str(
                    row.get("ID TICKET", "")
                ).strip()

                payload["entry.822984039"] = str(
                    row.get(
                        "Eskalasi Back Office",
                        ""
                    )
                ).strip()

                payload["entry.49503729"] = str(
                    row.get(
                        "Hasil Eskalasi",
                        "No respon"
                    )
                ).strip()

                # ==================
                # KETERANGAN
                # ==================

                ket = str(
                    row.get(
                        "Keterangan Tambahan",
                        "-"
                    )
                ).strip()

                if ket.lower() == "nan":
                    ket = "-"

                payload["entry.546067612"] = ket

                # ==================
                # PICK UP TIME
                # ==================

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

                # ==================
                # CREATE TICKET DATE
                # ==================

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

                # ==================
                # CREATE TICKET TIME
                # ==================

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

                # ==================
                # HIDDEN FIELD
                # ==================

                payload[
                    "entry.822984039_sentinel"
                ] = ""

                payload[
                    "entry.49503729_sentinel"
                ] = ""

                payload["fvv"] = "1"
                payload["pageHistory"] = "0"

                # fbzx random
                payload["fbzx"] = str(
                    abs(hash(str(idx)))
                )

                # ==================
                # DEBUG
                # ==================

                st.write(
                    f"Payload Baris {idx+1}"
                )

                st.json(payload)

                response = session.post(
                    FORM_URL,
                    data=payload,
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Referer":
                        FORM_URL.replace(
                            "formResponse",
                            "viewform"
                        )
                    },
                    timeout=30,
                    allow_redirects=True
                )

                st.write(
                    "Status:",
                    response.status_code
                )

                if response.status_code == 200:

                    sukses += 1

                else:

                    st.error(
                        f"Baris {idx+1} gagal ({response.status_code})"
                    )

                    st.text(
                        response.text[:1000]
                    )

                progress.progress(
                    (idx + 1) / len(df)
                )

            except Exception as e:

                st.error(
                    f"Baris {idx+1} error: {e}"
                )

        st.success(
            f"Selesai. Berhasil memproses {sukses} dari {len(df)} data."
        )
