import streamlit as st
from datetime import datetime, date
import pandas as pd

# --- Fungsi agregasi entri jurnal ---
def agregasi_entri(entri_list):
    hasil = {}
    for e in entri_list:
        akun = e["akun"]
        debit = e["debit"]
        kredit = e["kredit"]
        if akun not in hasil:
            hasil[akun] = {"akun": akun, "debit": 0.0, "kredit": 0.0}
        hasil[akun]["debit"] += debit
        hasil[akun]["kredit"] += kredit
    return list(hasil.values())

# --- CSS custom untuk UI ---
def local_css():
    st.markdown("""
        <style>
        /* Background dan font */
        body, .main {
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            color: #663300;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        /* Judul */
        h1, h2, h3, h4 {
            color: #994d00;
            font-weight: 700;
        }
        /* Button styling */
        div.stButton > button {
            background: linear-gradient(45deg, #ff8c1a, #e65c00);
            color: white;
            border-radius: 12px;
            padding: 0.6em 1.4em;
            font-weight: 700;
            font-size: 18px;
            border: none;
            box-shadow: 0 4px 12px rgba(230, 92, 0, 0.5);
            transition: all 0.3s ease;
            cursor: pointer;
            width: 100%;
            max-width: 280px;
            margin-top: 12px;
            margin-bottom: 12px;
            user-select: none;
        }
        div.stButton > button:hover {
            background: linear-gradient(45deg, #e65c00, #b34700);
            box-shadow: 0 6px 15px rgba(179, 71, 0, 0.8);
            transform: translateY(-2px);
        }
        /* Table styling */
        table {
            border-collapse: collapse;
            width: 100% !important;
            font-size: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        thead tr th {
            background-color: #ff6600 !important;
            color: white !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 12px 15px;
            text-align: left;
        }
        tbody tr {
            background-color: #fff7e6;
            transition: background-color 0.3s ease;
        }
        tbody tr:nth-child(even) {
            background-color: #ffe6cc;
        }
        tbody tr:hover {
            background-color: #ffcc99 !important;
        }
        tbody tr td {
            padding: 10px 15px;
            border-bottom: 1px solid #f0ad4e;
            color: #663300;
        }
        /* Inputs styling */
        div[data-baseweb="select"] > div {
            border-radius: 8px !important;
            border-color: #ff6600 !important;
        }
        /* Slider styling */
        .stSlider > div > div > div > div {
            accent-color: #ff6600 !important;
        }
        /* Markdown link styling */
        a {
            color: #ff6600;
            text-decoration: none;
            font-weight: 600;
        }
        a:hover {
            text-decoration: underline;
        }
        /* Checkbox label styling */
        div.stCheckbox > label > div[data-testid="stMarkdownContainer"] > p {
            font-weight: 600;
            color: #994d00;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Inisialisasi data session ---
def init_data():
    if "data" not in st.session_state:
        st.session_state.data = {
            "users": [],
            "orders": [],
            "feedbacks": [],
            "jurnal_umum": [],
            "next_id": 1
        }

# --- Daftar akun, metode pembayaran, dan ekspedisi ---
AKUN_LIST = [
    "Kas", "Bank", "Piutang", "Hutang", "Hutang Karyawan", "Hutang Pajak",
    "Pendapatan Penjualan", "Pendapatan dari Penjualan Perlengkapan", "Pendapatan dari Penjualan Tanah",
    "Pendapatan Saham",
    "Biaya Pakan", "Biaya Obat", "Biaya Listrik", "Biaya Air",
    "Beban Pokok Pendapatan", "Biaya Operasional",
    "Biaya Amortisasi Pajak", "Biaya Depresiasi Kendaraan", "Biaya Depresiasi Bangunan",
    "Biaya Pembelian Perlengkapan", "Biaya Pembelian Tanah",
    "Biaya Pembelian Kendaraan", "Biaya Pembelian Bangunan",
    "Biaya Dividen", "Persediaan"
]

metode_list = ["BRI", "BNI", "BCA", "BTN", "BJB", "MANDIRI",
               "BSI", "BANK MEGA", "BANK CIMB NIAGA", "BANK DANAMON"]
ekspedisi_list = ["JNT", "JNE", "Pos Indonesia", "Sicepat", "Anteraja", "Ninja Express"]

# --- Fungsi user management ---
def add_user(email, password, username, role='customer'):
    data = st.session_state.data
    users = data.get("users", [])
    for user in users:
        if user["email"].lower() == email.lower() or user["username"].lower() == username.lower():
            raise ValueError("Email atau username sudah terdaftar")
    users.append({"email": email, "password": password, "username": username, "role": role})

def validate_login(email, password):
    for user in st.session_state.data.get("users", []):
        if user["email"].lower() == email.lower() and user["password"] == password:
            return user
    return None

# --- Fungsi order dan feedback ---
def add_order(email, kg, jenis_kentang, alamat, metode_pembayaran, nomor_rekening, ekspedisi):
    data = st.session_state.data
    order = {
        "email": email, "kg": kg, "jenis_kentang": jenis_kentang, "alamat": alamat,
        "metode_pembayaran": metode_pembayaran, "nomor_rekening": nomor_rekening,
        "ekspedisi": ekspedisi
    }
    data["orders"].append(order)
    add_order_jurnal(order)

def add_feedback(email, rating):
    st.session_state.data["feedbacks"].append({"email": email, "rating": rating})

# --- Fungsi jurnal akuntansi ---
def add_order_jurnal(order):
    data = st.session_state.data
    harga_per_kg = 8700 if order['jenis_kentang'] == 'Kentang Kecil' else 10300
    total = order['kg'] * harga_per_kg
    tgl = datetime.now().strftime("%Y-%m-%d")
    deskripsi = f"Penjualan {order['jenis_kentang']} {order['kg']} kg ke {order['email']}"
    jurnal_id = data["next_id"]
    data["next_id"] += 1
    jurnal_entry = {
        "id": jurnal_id,
        "tanggal": tgl,
        "deskripsi": deskripsi,
        "entri": [
            {"akun": "Kas", "debit": float(total), "kredit": 0.0},
            {"akun": "Pendapatan Penjualan", "debit": 0.0, "kredit": float(total)}
        ]
    }
    data["jurnal_umum"].append(jurnal_entry)

# --- Fungsi tambah jurnal baru ---
def tambah_jurnal_baru(data):
    st.subheader("Tambah Jurnal Umum Baru")
    tanggal = st.date_input("Tanggal Transaksi", value=date.today())
    deskripsi = st.text_input("Deskripsi Jurnal")
    if "jumlah_entri" not in st.session_state:
        st.session_state.jumlah_entri = 1
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Tambah Baris Entri"):
            if st.session_state.jumlah_entri < 10:
                st.session_state.jumlah_entri += 1
    with col2:
        if st.button("Hapus Baris Entri"):
            if st.session_state.jumlah_entri > 1:
                st.session_state.jumlah_entri -= 1
    entri_baru = []
    for i in range(st.session_state.jumlah_entri):
        st.markdown(f"Entri #{i+1}")
        akun = st.selectbox(f"Akun #{i+1}", AKUN_LIST, key=f"akun_{i}")
        debit = st.number_input(f"Debit #{i+1}", min_value=0.0, format="%.2f", key=f"debit_{i}")
        kredit = st.number_input(f"Kredit #{i+1}", min_value=0.0, format="%.2f", key=f"kredit_{i}")
        entri_baru.append({"akun": akun, "debit": debit, "kredit": kredit})
    if st.button("Simpan Jurnal Baru"):
        total_debit = sum(e["debit"] for e in entri_baru)
        total_kredit = sum(e["kredit"] for e in entri_baru)
        if total_debit != total_kredit:
            st.error("Jumlah total Debit dan Kredit harus sama!")
            return
        if total_debit == 0:
            st.error("Setidaknya salah satu entri harus memiliki nilai Debit.")
            return
        if not deskripsi.strip():
            st.error("Deskripsi jurnal tidak boleh kosong.")
            return
        entri_terakumulasi = agregasi_entri(entri_baru)
        jurnal_baru = {
            "id": data["next_id"],
            "tanggal": tanggal.strftime("%Y-%m-%d"),
            "deskripsi": deskripsi,
            "entri": entri_terakumulasi
        }
        data["jurnal_umum"].append(jurnal_baru)
        data["next_id"] += 1
        st.success("Jurnal baru berhasil ditambahkan.")
        st.session_state.jumlah_entri = 1
        for i in range(10):
            for key in [f"akun_{i}", f"debit_{i}", f"kredit_{i}"]:
                if key in st.session_state:
                    del st.session_state[key]
        st.experimental_rerun()

# --- Fungsi edit jurnal ---
def edit_jurnal_form(data, jurnal_id):
    st.write("### Edit Jurnal")
    jurnal = next((j for j in data["jurnal_umum"] if j["id"] == jurnal_id), None)
    if not jurnal:
        st.error("Jurnal tidak ditemukan.")
        return
    tanggal = st.date_input("Tanggal", datetime.strptime(jurnal["tanggal"], "%Y-%m-%d").date(), key="edit_tanggal")
    deskripsi = st.text_input("Deskripsi", jurnal["deskripsi"], key="edit_deskripsi")
    entri = jurnal["entri"]
    for i, e in enumerate(entri):
        st.write(f"Entri #{i+1}")
        akun = st.selectbox("Akun", AKUN_LIST, index=AKUN_LIST.index(e["akun"]), key=f"edit_akun_{i}")
        debit = st.number_input("Debit", min_value=0.0, value=e["debit"], format="%.2f", key=f"edit_debit_{i}")
        kredit = st.number_input("Kredit", min_value=0.0, value=e["kredit"], format="%.2f", key=f"edit_kredit_{i}")
        entri[i] = {"akun": akun, "debit": debit, "kredit": kredit}
    if st.button("Simpan Perubahan"):
        total_debit = sum(e["debit"] for e in entri)
        total_kredit = sum(e["kredit"] for e in entri)
        if total_debit != total_kredit:
            st.error("Jumlah total Debit dan Kredit harus sama!")
            return
        if total_debit == 0:
            st.error("Setidaknya salah satu entri harus memiliki nilai Debit.")
            return
        if not deskripsi.strip():
            st.error("Deskripsi jurnal tidak boleh kosong.")
            return
        entri_terakumulasi = agregasi_entri(entri)
        jurnal["tanggal"] = tanggal.strftime("%Y-%m-%d")
        jurnal["deskripsi"] = deskripsi
        jurnal["entri"] = entri_terakumulasi
        st.success("Jurnal berhasil diperbarui.")
        del st.session_state["edit_jurnal_id"]
        st.experimental_rerun()

# --- Fungsi daftar jurnal umum ---
def jurnal_umum(data):
    st.subheader("Daftar Jurnal Umum")
    if "edit_jurnal_id" in st.session_state:
        edit_jurnal_form(data, st.session_state["edit_jurnal_id"])
        st.write("---")
    if not data["jurnal_umum"]:
        st.info("Belum ada jurnal umum.")
        return
    jurnal_urut = sorted(data["jurnal_umum"], key=lambda x: x["tanggal"], reverse=True)
    for jurnal in jurnal_urut:
        st.markdown(f"Tanggal: {jurnal['tanggal']}  |  Deskripsi: {jurnal['deskripsi']}")
        df_entri = pd.DataFrame(jurnal["entri"])
        def format_rp(x):
            return f"Rp {x:,.2f}" if x != 0 else ""
        df_entri["debit"] = df_entri["debit"].apply(format_rp)
        df_entri["kredit"] = df_entri["kredit"].apply(format_rp)
        df_entri.rename(columns={"akun": "Akun", "debit": "Debit (Rp)", "kredit": "Kredit (Rp)"}, inplace=True)
        st.table(df_entri)
        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("Edit", key=f"edit_{jurnal['id']}"):
                st.session_state["edit_jurnal_id"] = jurnal["id"]
                st.experimental_rerun()
        with cols[1]:
            if st.button("Hapus", key=f"hapus_{jurnal['id']}"):
                data["jurnal_umum"] = [j for j in data["jurnal_umum"] if j["id"] != jurnal["id"]]
                st.success("Jurnal berhasil dihapus.")
                st.experimental_rerun()
        st.markdown("---")

# --- Fungsi buku besar ---
def buku_besar(data):
    st.subheader("Buku Besar")
    if not data["jurnal_umum"]:
        st.info("Belum ada data jurnal umum.")
        return
    akun_set = set()
    for jurnal in data["jurnal_umum"]:
        for e in jurnal["entri"]:
            akun_set.add(e["akun"])
    daftar_akun = sorted(list(akun_set))
    akun_terpilih = st.selectbox("Pilih Akun", daftar_akun)
    jurnal_sorted = sorted(data["jurnal_umum"], key=lambda x: x["tanggal"])
    tgl_awal_default = datetime.strptime(jurnal_sorted[0]["tanggal"], "%Y-%m-%d").date() if jurnal_sorted else date.today()
    col1, col2 = st.columns(2)
    with col1:
        tgl_mulai = st.date_input("Dari Tanggal", value=tgl_awal_default)
    with col2:
        tgl_akhir = st.date_input("Sampai Tanggal", value=date.today())
    if tgl_akhir < tgl_mulai:
        st.warning("Tanggal akhir harus sama atau setelah tanggal mulai.")
        return
    entri_akun = []
    for jurnal in data["jurnal_umum"]:
        tgl = datetime.strptime(jurnal["tanggal"], "%Y-%m-%d").date()
        if not (tgl_mulai <= tgl <= tgl_akhir):
            continue
        for e in jurnal["entri"]:
            if e["akun"] == akun_terpilih:
                entri_akun.append({"tanggal": jurnal["tanggal"], "deskripsi": jurnal["deskripsi"], "debit": e["debit"], "kredit": e["kredit"]})
    if not entri_akun:
        st.warning(f"Tidak ada mutasi pada akun '{akun_terpilih}' untuk periode ini.")
        return
    akun_normal_debit = {
        "Kas", "Bank", "Piutang", "Persediaan",
        "Biaya Pakan", "Biaya Obat", "Biaya Listrik", "Biaya Air",
        "Beban Pokok Pendapatan", "Biaya Operasional",
        "Biaya Amortisasi Pajak", "Biaya Depresiasi Kendaraan", "Biaya Depresiasi Bangunan",
        "Biaya Pembelian Perlengkapan", "Biaya Pembelian Tanah",
        "Biaya Pembelian Kendaraan", "Biaya Pembelian Bangunan",
        "Biaya Dividen"
    }
    akun_normal_kredit = {
        "Hutang", "Hutang Karyawan", "Hutang Pajak",
        "Pendapatan Penjualan", "Pendapatan dari Penjualan Perlengkapan",
        "Pendapatan dari Penjualan Tanah", "Pendapatan Saham"
    }
    saldo = 0.0
    rows = []
    for e in sorted(entri_akun, key=lambda x: x["tanggal"]):
        if akun_terpilih in akun_normal_debit:
            saldo += e["debit"] - e["kredit"]
        elif akun_terpilih in akun_normal_kredit:
            saldo += e["kredit"] - e["debit"]
        else:
            saldo += e["debit"] - e["kredit"]
        rows.append({"Tanggal": e["tanggal"], "Deskripsi": e["deskripsi"], 
                     "Debit": f"Rp {e['debit']:,.2f}" if e["debit"] else "", 
                     "Kredit": f"Rp {e['kredit']:,.2f}" if e["kredit"] else "", 
                     "Saldo": f"Rp {saldo:,.2f}"})
    st.markdown(f"### Mutasi Akun: {akun_terpilih}")
    st.table(rows)

# --- Fungsi neraca saldo ---
def neraca_saldo(data):
    st.subheader("Neraca Saldo")
    if not data["jurnal_umum"]:
        st.info("Belum ada data jurnal umum.")
        return
    jurnal_sorted = sorted(data["jurnal_umum"], key=lambda x: x["tanggal"])
    tgl_awal_default = datetime.strptime(jurnal_sorted[0]["tanggal"], "%Y-%m-%d").date() if jurnal_sorted else date.today()
    col1, col2 = st.columns(2)
    with col1:
        tgl_mulai = st.date_input("Dari Tanggal", value=tgl_awal_default)
    with col2:
        tgl_akhir = st.date_input("Sampai Tanggal", value=date.today())
    if tgl_akhir < tgl_mulai:
        st.warning("Tanggal akhir harus sama atau setelah tanggal mulai.")
        return
    akun_set = set()
    for jurnal in data["jurnal_umum"]:
        for e in jurnal["entri"]:
            akun_set.add(e["akun"])
    saldo_per_akun = {akun: {"debit":0.0, "kredit":0.0} for akun in akun_set}
    for jurnal in data["jurnal_umum"]:
        tgl = datetime.strptime(jurnal["tanggal"], "%Y-%m-%d").date()
        if not (tgl_mulai <= tgl <= tgl_akhir):
            continue
        for e in jurnal["entri"]:
            saldo_per_akun[e["akun"]]["debit"] += e["debit"]
            saldo_per_akun[e["akun"]]["kredit"] += e["kredit"]
    rows = []
    total_debit = 0.0
    total_kredit = 0.0
    for akun in sorted(saldo_per_akun.keys()):
        debit = saldo_per_akun[akun]["debit"]
        kredit = saldo_per_akun[akun]["kredit"]
        saldo = debit - kredit
        saldo_debit = saldo if saldo > 0 else 0
        saldo_kredit = -saldo if saldo < 0 else 0
        total_debit += saldo_debit
        total_kredit += saldo_kredit
        rows.append({"Akun": akun, 
                     "Saldo Debit (Rp)": f"Rp {saldo_debit:,.2f}" if saldo_debit else "", 
                     "Saldo Kredit (Rp)": f"Rp {saldo_kredit:,.2f}" if saldo_kredit else ""})
    st.table(rows)
    st.markdown("---")
    st.write(f"Total Saldo Debit: Rp {total_debit:,.2f}")
    st.write(f"Total Saldo Kredit: Rp {total_kredit:,.2f}")
    if abs(total_debit - total_kredit) > 0.01:
        st.error("⚠ Neraca Saldo tidak seimbang! Total Debit tidak sama dengan Total Kredit.")
    else:
        st.success("Neraca Saldo seimbang (Total Debit = Total Kredit).")

# --- Fungsi laporan laba rugi ---
def laporan_laba_rugi(data):
    st.subheader("Laporan Laba Rugi Rinci")
    st.markdown("Untuk Periode yang berakhir")
    jurnal_sorted = sorted(data["jurnal_umum"], key=lambda x: x["tanggal"])
    if not jurnal_sorted:
        st.info("Belum ada data jurnal umum.")
        return
    tgl_awal_default = datetime.strptime(jurnal_sorted[0]["tanggal"], "%Y-%m-%d").date()
    col1, col2 = st.columns(2)
    with col1:
        tgl_mulai = st.date_input("Dari Tanggal", value=tgl_awal_default)
    with col2:
        tgl_akhir = st.date_input("Sampai Tanggal", value=date.today())
    if tgl_akhir < tgl_mulai:
        st.warning("Tanggal akhir harus sama atau setelah tanggal mulai.")
        return
    akun_pendapatan = {"Pendapatan Penjualan", 
                       "Pendapatan dari Penjualan Perlengkapan", 
                       "Pendapatan dari Penjualan Tanah", 
                       "Pendapatan Saham"}
    akun_harga_pokok = {
        "Beban Pokok Pendapatan", "Biaya Pembelian Perlengkapan", "Biaya Pembelian Tanah", 
        "Biaya Pembelian Kendaraan", "Biaya Pembelian Bangunan", "Persediaan"
    }
    akun_beban_operasional = {
        "Biaya Pakan", "Biaya Obat", "Biaya Listrik", "Biaya Air", "Biaya Operasional",
        "Biaya Amortisasi Pajak", "Biaya Depresiasi Kendaraan", "Biaya Depresiasi Bangunan",
        "Biaya Dividen"
    }
    total_pendapatan = 0.0
    total_harga_pokok = 0.0
    total_beban_operasional = 0.0
    for jurnal in data["jurnal_umum"]:
        tgl = datetime.strptime(jurnal["tanggal"], "%Y-%m-%d").date()
        if not (tgl_mulai <= tgl <= tgl_akhir):
            continue
        for e in jurnal["entri"]:
            akun = e["akun"]
            debit = e["debit"]
            kredit = e["kredit"]
            if akun in akun_pendapatan:
                total_pendapatan += kredit - debit
            elif akun in akun_harga_pokok:
                total_harga_pokok += debit - kredit
            elif akun in akun_beban_operasional:
                total_beban_operasional += debit - kredit
    laba_kotor = total_pendapatan - total_harga_pokok
    laba_bersih = laba_kotor - total_beban_operasional
    laba_str = f"Rp {abs(laba_bersih):,.2f}"
    warna = "green" if laba_bersih >= 0 else "red"
    status = "Laba Bersih" if laba_bersih >= 0 else "Rugi Bersih"
    df = pd.DataFrame([
        ["Pendapatan", f"Rp {total_pendapatan:,.2f}"],
        ["Harga Pokok Penjualan", f"Rp {total_harga_pokok:,.2f}"],
        ["Laba Kotor", f"Rp {laba_kotor:,.2f}"],
        ["Biaya Operasional", f"Rp {total_beban_operasional:,.2f}"],
        [status, f"<span style='color:{warna}; font-weight:bold;'>{laba_str}</span>"]
    ], columns=["Keterangan", "Nilai (Rp)"])
    st.write("### Detail Laporan Laba Rugi")
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

# --- Fungsi utama aplikasi ---
def app():
    init_data()
    local_css()

    if "step" not in st.session_state:
        st.session_state.step = 0
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "role" not in st.session_state:
        st.session_state.role = ""

    if st.session_state.step == 0:
        st.write('Hello! Welcome to Potago!')

        login_as = st.radio('Login sebagai:', ['Customer', 'Admin'], index=0, key='login_as')

        if login_as == 'Customer':
            option = st.selectbox('Login / Sign Up', ['Login', 'Sign Up'], key='login_signup_option')
            if option == 'Login':
                email = st.text_input('Email Address', key='login_email')
                password = st.text_input('Password', type='password', key='login_password')
                if st.button('Login'):
                    user = validate_login(email, password)
                    if user:
                        st.success('Login Berhasil sebagai Customer!')
                        st.session_state.email = email
                        st.session_state.username = user["username"]
                        st.session_state.role = user["role"]
                        st.session_state.step = 1
                    else:
                        st.error("Email atau Password salah.")
            else:
                email = st.text_input('Email Address', key='signup_email')
                password = st.text_input('Password', type='password', key='signup_password')
                username = st.text_input('Enter your unique username', key='signup_username')
                if st.button('Sign Up'):
                    try:
                        add_user(email, password, username)
                        st.success("Sign Up berhasil! Silakan login.")
                    except Exception as e:
                        st.error(f"Error: {e}")

        else:
            email_admin = st.text_input('Email Admin', key='admin_email')
            password_admin = st.text_input('Password Admin', type='password', key='admin_password')
            if st.button('Login sebagai Admin'):
                if email_admin == "Potago.id" and password_admin == "adminpotago":
                    st.success("Login Berhasil sebagai Admin!")
                    st.session_state.email = email_admin
                    st.session_state.username = "Admin"
                    st.session_state.role = "admin"
                    st.session_state.step = 1
                else:
                    st.error("Email atau Password Admin salah.")

    elif st.session_state.step == 1:
        st.write(f"Selamat datang, {st.session_state.username}!")
        if st.session_state.role == "admin":
            st.title("Halaman Admin - Sistem Akuntansi")
            menu = st.selectbox("Pilih Menu Akuntansi:", [
                "Tambah Jurnal Umum",
                "Daftar Jurnal Umum",
                "Buku Besar",
                "Neraca Saldo",
                "Laporan Laba Rugi"
            ])

            data = st.session_state.data
            if menu == "Tambah Jurnal Umum":
                tambah_jurnal_baru(data)
            elif menu == "Daftar Jurnal Umum":
                jurnal_umum(data)
            elif menu == "Buku Besar":
                buku_besar(data)
            elif menu == "Neraca Saldo":
                neraca_saldo(data)
            elif menu == "Laporan Laba Rugi":
                laporan_laba_rugi(data)

            if st.button("Logout"):
                for key in ['step', 'email', 'username', 'role']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.experimental_rerun()
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("images/logo.png", width=300)
            st.write('Hello! Welcome to Potago!')
            st.title('Know more about us here!✦🥔')
            st.write('Info ladang kami')
            st.write("- Dipanen di strategi yang cocok, tepatnya di lereng Gunung Merbabu daerah Kopeng")
            st.write("- Memiliki total luas lahan seluas 1,5 hektar (15.000 m²)")
            st.write("- Dalam satu tahun kami bisa panen 3-4 kali dalam setahun (1 musim bisa 1-2x panen)")
            st.write("- Kami menanam di 2 waktu yang berbeda untuk menghindari kemungkinan gagal panen:")

            col1, col2 = st.columns([2,1])
            with col1:
                st.write("Penanaman 14 hari dari 80 hari untuk panen")
            with col2:
                st.image("images/15 hari.jpg", caption='Tanaman kentang umur 14 hari', width=250)
            col1, col2 = st.columns([2,1])
            with col1:
                st.write("Penanaman 50 hari dari 80 hari untuk panen")
            with col2:
                st.image("images/50 hari.jpg", caption='Tanaman kentang umur 50 hari', width=250)

            if st.button('Pembelian'):
                st.session_state.step = 2

    elif st.session_state.step == 2:
        st.write('Jumlah Pemesanan')
        st.session_state.kg = st.slider(
            "Pesan berapa banyak?", 0, 100,
            value=st.session_state.get('kg', 0),
            key='slider_kg'
        )
        st.write("Saya memesan", st.session_state.kg, "kg")

        st.session_state.jenis_kentang = st.radio(
            "Jenis Kentang",
            ["Kentang Besar", "Kentang Kecil"],
            index=["Kentang Besar", "Kentang Kecil"].index(st.session_state.get('jenis_kentang', "Kentang Besar")),
            key='radio_jenis_kentang'
        )

        col1, col2 = st.columns(2)
        with col1:
            st.image("images/kentang kecil.jpg", caption='Rp 8.700', width=250)
        with col2:
            st.image("images/kentang besar.jpg", caption='Rp 10.300', width=250)

        st.session_state.alamat = st.text_input(
            'Alamat Tujuan',
            value=st.session_state.get('alamat', ""),
            placeholder="Masukkan alamat kemana barang akan dituju",
            key='input_alamat'
        )

        col_back, col_next = st.columns(2)
        with col_back:
            if st.button('Back'):
                st.session_state.step = 1
        with col_next:
            if st.button('Pembayaran'):
                if st.session_state.kg > 0 and st.session_state.alamat.strip() != "":
                    st.session_state.step = 3
                else:
                    st.error("Mohon isi jumlah pemesanan dan alamat tujuan dengan benar.")

    elif st.session_state.step == 3:
        st.session_state.metode_pembayaran = st.selectbox(
            'Metode Pembayaran',
            metode_list,
            index=metode_list.index(st.session_state.get('metode_pembayaran', metode_list[0])),
            key='select_metode'
        )
        st.session_state.nomor_rekening = st.text_input(
            "Masukkan nomor rekening anda",
            value=st.session_state.get('nomor_rekening', ""),
            key='input_rekening'
        )
        st.session_state.ekspedisi = st.selectbox(
            'Ekspedisi Pengiriman',
            ekspedisi_list,
            index=ekspedisi_list.index(st.session_state.get('ekspedisi', ekspedisi_list[0])),
            key='select_ekspedisi'
        )

        col_back, col_next = st.columns(2)
        with col_back:
            if st.button('Back'):
                st.session_state.step = 2
        with col_next:
            if st.button('Next'):
                if st.session_state.nomor_rekening.strip() != "":
                    st.session_state.step = 4
                else:
                    st.error("Mohon masukkan nomor rekening anda.")

    elif st.session_state.step == 4:
        st.title("Konfirmasi Pesanan Anda")
        st.write("Harap periksa kembali data berikut sebelum melanjutkan:")

        st.markdown(f"Email: {st.session_state.email}")
        st.markdown(f"Jumlah Kentang (kg): {st.session_state.kg}")
        st.markdown(f"Jenis Kentang: {st.session_state.jenis_kentang}")
        st.markdown(f"Alamat Tujuan: {st.session_state.alamat}")
        st.markdown(f"Metode Pembayaran: {st.session_state.metode_pembayaran}")
        st.markdown(f"Nomor Rekening: {st.session_state.nomor_rekening}")
        st.markdown(f"Ekspedisi Pengiriman: {st.session_state.ekspedisi}")

        confirmed = st.checkbox("Saya sudah memastikan data di atas sudah benar", key="confirm_checkbox")

        col_back, col_submit = st.columns(2)
        with col_back:
            if st.button("Back"):
                st.session_state.step = 3
        with col_submit:
            if st.button("Submit Order"):
                if confirmed:
                    add_order(
                        email=st.session_state.email,
                        kg=st.session_state.kg,
                        jenis_kentang=st.session_state.jenis_kentang,
                        alamat=st.session_state.alamat,
                        metode_pembayaran=st.session_state.metode_pembayaran,
                        nomor_rekening=st.session_state.nomor_rekening,
                        ekspedisi=st.session_state.ekspedisi,
                    )
                    st.success("Pesanan berhasil dikirim! Terima kasih.")
                    st.session_state.step = 5
                    for key in ['kg', 'jenis_kentang', 'alamat', 'metode_pembayaran',
                                'nomor_rekening', 'ekspedisi', 'confirm_checkbox']:
                        if key in st.session_state:
                            del st.session_state[key]
                else:
                    st.error("Mohon centang konfirmasi sebelum Submit.")

    elif st.session_state.step == 5:
        st.title('Terima Kasih telah berbelanja di toko kami :)')
        st.write('Have a nice day!')

        rating = st.radio("Berikan rating untuk kami:", ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'], key='feedback_rating')

        if st.button('Kirim Feedback'):
            add_feedback(email=st.session_state.email, rating=rating)
            st.success("Feedback berhasil dikirim!")

        col1, col2 = st.columns(2)
        with col1:
            if st.button('Logout'):
                keys_to_clear = ['step', 'email', 'username', 'role', 'kg', 'jenis_kentang',
                                 'alamat', 'metode_pembayaran', 'nomor_rekening', 'ekspedisi',
                                 'confirm_checkbox', 'feedback_rating']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.experimental_rerun()

        with col2:
            if st.button('Belanja Lagi'):
                st.session_state.step = 1
                for key in ['kg', 'jenis_kentang', 'alamat', 'metode_pembayaran', 'nomor_rekening',
                            'ekspedisi', 'confirm_checkbox', 'feedback_rating']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.experimental_rerun()

if __name__ == "__main__":
    app()