# 🧾 Digital Receipt Generator Pro

Aplikasi web interaktif berbasis **Streamlit** untuk membuat, mengkustomisasi, dan mengunduh kwitansi pembayaran digital secara instan. Mendukung berbagai ukuran kertas, skema warna usaha, hingga ekspor dokumen ke berbagai format.

---

## ✨ Fitur Utama

* **📐 Multi-Ukuran Kertas & Orientasi**: Mendukung format A4 & A5 (Landscape & Portrait) serta Struk Thermal 80mm (Kasir) yang secara otomatis terkunci presisi dalam 1 halaman.
* **📥 Export Multi-Format**: 
  * **PDF**: Siap cetak dengan tata letak profesional.
  * **PNG**: Gambar siap kirim via WhatsApp / Chat.
  * **Excel (.xlsx)**: Rekap data kwitansi lengkap dengan rumus perhitungan otomatis.
* **🎨 Custom Branding & Tema**:
  * Fitur unggah logo toko/perusahaan.
  * Pilihan preset warna (Classic Blue, Forest Green, Elegant Charcoal, Crimson Red).
* **👁️ Live Preview**: Pratinjau kwitansi secara *real-time* langsung di browser sebelum diunduh.
* **🔢 Perhitungan Otomatis**: Tabel barang dinamis dengan akumulasi subtotal dan total bayar otomatis.

---

## 🛠️ Teknologi yang Digunakan

* **Python 3.9+**
* **Streamlit** (Interface Web Framework)
* **ReportLab** (Engine Pembentuk PDF)
* **Pandas & XlsxWriter** (Pengolahan Data & Ekspor Excel)
* **pdf2image & Pillow** (Konversi PDF ke Gambar PNG)

---

## 🚀 Panduan Instalasi & Penggunaan

### 1. Clone Repository
```bash
git clone [https://github.com/username-kamu/digital-receipt-generator.git](https://github.com/username-kamu/digital-receipt-generator.git)
cd digital-receipt-generator
