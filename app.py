import streamlit as st
import pandas as pd
import requests
import time
import random
import traceback

from datetime import datetime
from datetime import timedelta
from datetime import time as dt_time

# =====================================================
# GOOGLE FORM
# =====================================================

FORM_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdYY2hbRIhrCY_a06uH0keEsBBu8x6P3AzpZ2BmcmVERjaxpQ/formResponse"

# =====================================================
# SESSION STATE
# =====================================================

if "last_success" not in st.session_state:
    st.session_state.last_success = 0

# =====================================================
# HELPER
# =====================================================

def clean_value(val):

    if pd.isna(val):
        return ""

    return str(val).strip()


def parse_time_excel(value):

    if pd.isna(value):
        return None

    try:

        if isinstance(value, dt_time):
            return value.strftime("%H:%M:%S")

        if isinstance(value, datetime):
            return value.strftime("%H:%M:%S")

        value = str(value).strip()

        if value == "":
            return None

        if " " in value:
            value = value.split(" ")[-1]

        if "." in value:
            value = value.split(".")[0]

        dt = pd.to_datetime(value)

        return dt.strftime("%H:%M:%S")

    except:
        return None


def generate_pickup_time(create_time, delay_minutes):

    try:

        dt = datetime.strptime(
            create_time,
            "%H:%M:%S"
        )

        pickup = dt - timedelta(
            minutes=delay_minutes
        )

        return pickup.strftime("%H:%M:%S")

    except:
        return None


def build_payload(
    row,
    pickup_mode,
    delay_mode,
    fixed_delay,
    min_delay,
    max_delay
):

    payload = {}

    payload["entry.154565194"] = clean_value(
        row.get("Nama")
    )

    payload["entry.1778899713"] = clean_value(
        row.get("SBU")
    )

    payload["entry.1802806380"] = clean_value(
        row.get("ID TICKET")
    )

    payload["entry.822984039"] = clean_value(
        row.get("Eskalasi Back Office")
    )

    payload["entry.49503729"] = (
        clean_value(
            row.get("Hasil Eskalasi")
        ) or "No respon"
    )

    payload["entry.564067612"] = (
        clean_value(
            row.get("Keterangan Tambahan")
        ) or "-"
    )

    # =================================================
    # PICKUP TIME
    # =================================================

    pickup = None

    if pickup_mode == "Generate Otomatis":

        create_time = parse_time_excel(
            row.get("Create Ticket Time")
        )

        if create_time:

            if delay_mode == "Tetap":

                delay = fixed_delay

            else:

                delay = random.randint(
                    min_delay,
                    max_delay
                )

            pickup = generate_pickup_time(
                create_time,
                delay
            )

    else:

        pickup = parse_time_excel(
            row.get("Pick Up Time")
        )

    if pickup:

        h, m, s = pickup.split(":")

        payload["entry.141665543_hour"] = h
        payload["entry.141665543_minute"] = m
        payload["entry.141665543_second"] = s

    # =================================================
    # CREATE DATE
    # =================================================

    try:

        tanggal = pd.to_datetime(
            row.get("Create Ticket Date"),
            dayfirst=True
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

    # =================================================
    # CREATE TIME
    # =================================================

    create_time = parse_time_excel(
        row.get("Create Ticket Time")
    )

    if create_time:

        h, m, s = create_time.split(":")

        payload["entry.2062984122_hour"] = h
        payload["entry.2062984122_minute"] = m
        payload["entry.2062984122_second"] = s

    return payload


# =====================================================
# UI
# =====================================================

st.set_page_config(
    page_title="Excel ➜ Google Form Importer",
    layout="wide"
)

st.title("Excel ➜ Google Form Importer")

# =====================================================
# PICKUP SETTING
# =====================================================

st.subheader("Pengaturan Pick Up Time")

pickup_mode = st.radio(
    "Mode Pick Up Time",
    [
        "Gunakan dari Excel",
        "Generate Otomatis"
    ]
)

delay_mode = "Tetap"
fixed_delay = 1
min_delay = 1
max_delay = 3

if pickup_mode == "Generate Otomatis":

    delay_mode = st.radio(
        "Jenis Jeda",
        [
            "Tetap",
            "Acak"
        ]
    )

    if delay_mode == "Tetap":

        fixed_delay = st.selectbox(
            "Kurangi Berapa Menit",
            [1, 2, 3],
            index=0
        )

    else:

        min_delay = st.number_input(
            "Jeda Minimum",
            min_value=1,
            max_value=10,
            value=1
        )

        max_delay = st.number_input(
            "Jeda Maksimum",
            min_value=min_delay,
            max_value=10,
            value=3
        )

# =====================================================
# DELAY ANTAR REQUEST
# =====================================================

max_delay_request = st.slider(
    "Jeda Maksimum Antar Data (detik)",
    1,
    30,
    20
)

file = st.file_uploader(
    "Upload Excel",
    type=["xlsx"]
)

col1, col2 = st.columns(2)

with col1:

    if st.button("Reset Progress"):

        st.session_state.last_success = 0

        st.success("Progress direset")

with col2:

    st.info(
        f"Baris terakhir berhasil : "
        f"{st.session_state.last_success}"
    )

# =====================================================
# LOAD FILE
# =====================================================

if file:

    df = pd.read_excel(file)

    df = df.dropna(how="all")

    # =============================================
    # PREVIEW PICKUP
    # =============================================

    preview_df = df.copy()

    if (
        pickup_mode == "Generate Otomatis"
        and "Create Ticket Time" in preview_df.columns
    ):

        preview_pickup = []

        for _, row in preview_df.iterrows():

            create_time = parse_time_excel(
                row.get("Create Ticket Time")
            )

            if create_time:

                if delay_mode == "Tetap":

                    delay = fixed_delay

                else:

                    delay = random.randint(
                        min_delay,
                        max_delay
                    )

                preview_pickup.append(
                    generate_pickup_time(
                        create_time,
                        delay
                    )
                )

            else:

                preview_pickup.append("")

        preview_df[
            "Preview Pick Up Time"
        ] = preview_pickup

    st.dataframe(preview_df.head(20))

    st.write(
        f"Total data : {len(df)}"
    )

    if st.button("Kirim ke Google Form"):

        progress = st.progress(0)

        status_box = st.empty()

        sukses = 0
        gagal = 0

        session = requests.Session()

        start_row = st.session_state.last_success

        for nomor in range(
            start_row,
            len(df)
        ):

            row = df.iloc[nomor]

            try:

                payload = build_payload(
                    row,
                    pickup_mode,
                    delay_mode,
                    fixed_delay,
                    min_delay,
                    max_delay
                )

                response = session.post(
                    FORM_URL,
                    data=payload,
                    headers={
                        "User-Agent":
                        "Mozilla/5.0"
                    },
                    timeout=60
                )

                if response.status_code in [200, 302]:

                    sukses += 1

                    st.session_state.last_success = (
                        nomor + 1
                    )

                    status_box.success(
                        f"✓ Baris {nomor+1} berhasil"
                    )

                else:

                    gagal += 1

                    status_box.error(
                        f"✗ Baris {nomor+1} gagal"
                    )

                progress.progress(
                    (nomor + 1)
                    / len(df)
                )

                if nomor < len(df) - 1:

                    delay_request = random.randint(
                        max(
                            3,
                            max_delay_request // 3
                        ),
                        max_delay_request
                    )

                    time.sleep(
                        delay_request
                    )

            except Exception as e:

                gagal += 1

                st.error(
                    f"""
Baris {nomor+1} ERROR

{str(e)}

{traceback.format_exc()}
"""
                )

        st.success(
            f"""
SELESAI

Berhasil : {sukses}
Gagal : {gagal}
Total : {len(df)}
"""
        )
