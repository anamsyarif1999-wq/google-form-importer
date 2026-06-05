import streamlit as st
import pandas as pd
import requests
import time

# URL Google Form
FORM_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdYY2hbRIhrCY_a06uH0keEsBBu8x6P3AzpZ2BmcmVERjaxpQ/formResponse"

st.title("Excel ➜ Google Form Importer")

# Setting delay
delay = st.number_input(
    "Jeda antar data (detik)",
    min_value=0,
    max_value=3600,
    value=30,
    step=1
)

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

        status_box = st.empty()

        sukses = 0

        session = requests.Session()

        for idx, row in df.iterrows():

            try:

                payload = {}

                # ==================
                # FIELD TEXT
                # ==================

                payload["entry.154565194"] = str(
                    row.get("Nama", "")
                ).strip()

                payload["entry.1778899713"] = str(
                    row.get("SBU", "")
                ).strip()

                payload["entry.1802806380"] = str(
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
                        ""
                    )
                ).strip()

                # ==================
                # KETERANGAN TAMBAHAN
                # ==================

                ket = str(
                    row.get(
                        "Keterangan Tambahan",
                        "-"
                    )
                ).strip()

                if ket.lower() == "nan":
                    ket = "-"

                payload["entry.564067612"] = ket

                # ==================
                # PICK UP TIME
                # ==================

                try:

                    pickup = str(
                        row.get(
                            "Pick Up Time",
                            ""
                        )
                    ).strip()

                    if pickup and ":" in pickup:

                        h, m, s = pickup.split(":")

                        payload["entry.141665543_hour"] = h
                        payload["entry.141665543_minute"] = m
                        payload["entry.141665543_second"] = s

                except:
                    pass

                # ==================
                # CREATE TICKET DATE
                # ==================

                try:

                    tanggal = pd.to_datetime(
                        row.get(
                            "Create Ticket Date"
                        )
                    )

                    payload["entry.1418866853_day"] = str(
                        tanggal.day
                    )

                    payload["entry.1418866853_month"] = str(
                        tanggal.month
                    )

                    payload["entry.1418866853_year"] = str(
                        tanggal.year
                    )

                except:
                    pass

                # ==================
                # CREATE TICKET TIME
                # ==================

                try:

                    jam = str(
                        row.get(
                            "Create Ticket Time",
                            ""
                        )
                    ).strip()

                    if jam and ":" in jam:

                        h, m, s = jam.split(":")

                        payload["entry.2062984122_hour"] = h
                        payload["entry.2062984122_minute"] = m
                        payload["entry.2062984122_second"] = s

                except:
                    pass

                # ==================
                # HIDDEN FIELD
                # ==================

                payload["entry.822984039_sentinel"] = ""
                payload["entry.49503729_sentinel"] = ""

                payload["fvv"] = "1"
                payload["pageHistory"] = "0"

                # ==================
                # KIRIM DATA
                # ==================

                response = session.post(
                    FORM_URL,
                    data=payload,
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Referer": FORM_URL.replace(
                            "formResponse",
                            "viewform"
                        )
                    },
                    timeout=30,
                    allow_redirects=True
                )

                if response.status_code == 200:

                    sukses += 1

                    status_box.success(
                        f"Data {idx+1}/{len(df)} berhasil dikirim | ID Ticket: {row.get('ID TICKET','')}"
                    )

                else:

                    status_box.error(
                        f"Baris {idx+1} gagal ({response.status_code})"
                    )

                progress.progress(
                    (idx + 1) / len(df)
                )

                # ==================
                # DELAY
                # ==================

                if idx < len(df) - 1 and delay > 0:

                    status_box.info(
                        f"Menunggu {delay} detik sebelum data berikutnya..."
                    )

                    time.sleep(delay)

            except Exception as e:

                st.error(
                    f"Baris {idx+1} error: {e}"
                )

        st.success(
            f"Selesai. Berhasil mengirim {sukses} dari {len(df)} data."
        )
