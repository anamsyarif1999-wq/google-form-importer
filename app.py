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

            payload = {

                # Nama
                "entry.1778972854": str(
                    row.get("Nama", "")
                ).strip(),

                # ID TICKET
                "entry.1131610637": str(
                    row.get("ID TICKET", "")
                ).strip(),

                # SBU
                "entry.1847893431": str(
                    row.get("SBU", "")
                ).strip(),

                # Eskalasi Back Office
                "entry.2054975984": str(
                    row.get("Eskalasi Back Office", "")
                ).strip(),

                # Hasil Eskalasi
                "entry.1035810770": str(
                    row.get("Hasil Eskalasi", "")
                ).strip(),
            }

            # =========================
            # KETERANGAN TAMBAHAN
            # =========================

            if "Keterangan Tambahan" in df.columns:

                ket = str(
                    row.get("Keterangan Tambahan", "")
                ).strip()

                if ket:
                    payload["entry.1789051105"] = ket

            # =========================
            # PICK UP TIME
            # =========================

            try:

                pickup = row.get("Pick Up Time")

                if pd.notna(pickup):

                    pickup = pd.to_datetime(
                        str(pickup),
                        errors="coerce"
                    )

                    if pd.notna(pickup):

                        payload["entry.1083825887_hour"] = f"{pickup.hour:02d}"
                        payload["entry.1083825887_minute"] = f"{pickup.minute:02d}"
                        payload["entry.1083825887_second"] = f"{pickup.second:02d}"

            except Exception as e:
                st.write(f"Pickup Time error: {e}")

            # =========================
            # CREATE TICKET DATE
            # =========================

            try:

                tanggal = pd.to_datetime(
                    row.get("Create Ticket Date"),
                    errors="coerce"
                )

                if pd.notna(tanggal):

                    payload["entry.405968346_day"] = str(tanggal.day)
                    payload["entry.405968346_month"] = str(tanggal.month)
                    payload["entry.405968346_year"] = str(tanggal.year)

            except Exception as e:
                st.write(f"Date error: {e}")

            # =========================
            # CREATE TICKET TIME
            # =========================

            try:

                jam = row.get("Create Ticket Time")

                if pd.notna(jam):

                    jam = pd.to_datetime(
                        str(jam),
                        errors="coerce"
                    )

                    if pd.notna(jam):

                        payload["entry.1785211983_hour"] = f"{jam.hour:02d}"
                        payload["entry.1785211983_minute"] = f"{jam.minute:02d}"
                        payload["entry.1785211983_second"] = f"{jam.second:02d}"

            except Exception as e:
                st.write(f"Time error: {e}")

            try:

                response = requests.post(
                    FORM_URL,
                    data=payload,
                    headers={
                        "User-Agent": "Mozilla/5.0"
                    },
                    timeout=20,
                    allow_redirects=False
                )

                st.write(
                    f"Baris {idx+1} | Status: {response.status_code}"
                )

                if response.status_code in [200, 302, 303]:

                    sukses += 1

                else:

                    st.error(
                        f"Baris {idx+1} gagal"
                    )

                    st.write("Payload:")
                    st.json(payload)

                    st.write("Response:")
                    st.text(response.text[:2000])

            except Exception as e:

                st.error(
                    f"Baris {idx+1} error: {e}"
                )

            progress.progress(
                (idx + 1) / len(df)
            )

        st.success(
            f"Selesai. Berhasil memproses {sukses} data."
        )
```
