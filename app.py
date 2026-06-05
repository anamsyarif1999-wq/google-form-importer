import streamlit as st
import pandas as pd
import requests

FORM_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdYY2hbRIhrCY_a06uH0keEsBBu8x6P3AzpZ2BmcmVERjaxpQ/formResponse"

st.title("Excel ➜ Google Form Importer")

file = st.file_uploader(
    "Upload Excel",
    type=["xlsx"]
)

def parse_time(value):
    try:
        if pd.isna(value):
            return None

        if hasattr(value, "hour"):
            return (
                f"{value.hour:02d}",
                f"{value.minute:02d}",
                f"{value.second:02d}"
            )

        text = str(value).strip()

        if ":" in text:
            parts = text.split(":")
            if len(parts) >= 3:
                return (
                    parts[0].zfill(2),
                    parts[1].zfill(2),
                    parts[2].zfill(2)
                )

        return None

    except:
        return None


if file:

    df = pd.read_excel(file)

    st.subheader("Preview Data")
    st.dataframe(df.head())

    st.write(f"Total data: {len(df)}")

    required_columns = [
        "Nama",
        "SBU",
        "ID TICKET",
        "Eskalasi Back Office",
        "Pick Up Time",
        "Create Ticket Date",
        "Create Ticket Time",
        "Hasil Eskalasi"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        st.error(
            "Kolom tidak ditemukan: "
            + ", ".join(missing)
        )
        st.stop()

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

                if (
                    ket
                    and ket.lower() != "nan"
                ):
                    payload[
                        "entry.546067612"
                    ] = ket

            # ======================
            # Pick Up Time
            # ======================

            pickup = parse_time(
                row.get("Pick Up Time")
            )

            if pickup:

                h, m, s = pickup

                payload[
                    "entry.141665543_hour"
                ] = h

                payload[
                    "entry.141665543_minute"
                ] = m

                payload[
                    "entry.141665543_second"
                ] = s

            # ======================
            # Create Ticket Date
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
            # Create Ticket Time
            # ======================

            jam = parse_time(
                row.get(
                    "Create Ticket Time"
                )
            )

            if jam:

                h, m, s = jam

                payload[
                    "entry.2062984122_hour"
                ] = h

                payload[
                    "entry.2062984122_minute"
                ] = m

                payload[
                    "entry.2062984122_second"
                ] = s

            try:

                response = session.post(
                    FORM_URL,
                    data=payload,
                    headers={
                        "User-Agent":
                        "Mozilla/5.0"
                    },
                    timeout=30,
                    allow_redirects=True
                )

                if response.status_code == 200:
                    sukses += 1

                else:

                    st.error(
                        f"Baris {idx+1} gagal "
                        f"({response.status_code})"
                    )

                    st.json(payload)

                    st.stop()

            except Exception as e:

                st.error(
                    f"Baris {idx+1} error: {e}"
                )

                st.stop()

            progress.progress(
                (idx + 1) / len(df)
            )

        st.success(
            f"Selesai. Berhasil mengirim "
            f"{sukses} dari {len(df)} data."
        )

        st.info(
            "Jika data masih tidak muncul "
            "di spreadsheet, kemungkinan "
            "Google Form tersebut tidak "
            "terhubung ke spreadsheet yang "
            "sedang Anda lihat atau "
            "memerlukan field tambahan "
            "yang tidak terlihat."
        )
