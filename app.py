import streamlit as st
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from datetime import date

# --- CONFIG PAGE ---
st.set_page_config(page_title="Digital Receipt Generator", page_icon="🧾", layout="centered")

st.title("🧾 Digital Receipt Generator")
st.caption("Buat dan unduh kwitansi PDF yang rapi & presisi tanpa masalah rendering CSS.")

# --- FORM INPUT ---
with st.form("receipt_form"):
    col1, col2 = st.columns(2)
    with col1:
        no_kwitansi = st.text_input("No. Kwitansi", "KW-2026/08/001")
        terima_dari = st.text_input("Telah Terima Dari", "PT Maju Bersama")
        tanggal = st.date_input("Tanggal Transaksi", date.today())
    with col2:
        nominal = st.number_input("Nominal (Rp)", min_value=0, value=1500000, step=50000)
        terbilang = st.text_input("Terbilang", "Satu Juta Lima Ratus Ribu Rupiah")
        penerima = st.text_input("Nama Penerima", "Budi Santoso")
        
    keperluan = st.text_area("Untuk Pembayaran", "Pembelian 1 Unit Laptop Asus & Lisensi Software")
    
    submitted = st.form_submit_button("🔨 Generate PDF Kwitansi")

# --- PDF GENERATOR (REPORTLAB) ---
def generate_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A5),
        rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#22303F'),
        spaceAfter=10
    )
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('BoldStyle', parent=normal_style, fontName='Helvetica-Bold')

    elements = []

    # Header
    elements.append(Paragraph("<b>KWITANSI PEMBAYARAN</b>", title_style))
    elements.append(Spacer(1, 10))

    # Table Content
    data = [
        [Paragraph("<b>No. Kwitansi</b>", normal_style), Paragraph(f": {no_kwitansi}", normal_style)],
        [Paragraph("<b>Telah Terima Dari</b>", normal_style), Paragraph(f": {terima_dari}", normal_style)],
        [Paragraph("<b>Uang Sejumlah</b>", normal_style), Paragraph(f": <i>{terbilang}</i>", normal_style)],
        [Paragraph("<b>Untuk Pembayaran</b>", normal_style), Paragraph(f": {keperluan}", normal_style)],
        [Paragraph("<b>Jumlah Rp</b>", normal_style), Paragraph(f": <b>Rp {nominal:,.0f}</b>", bold_style)],
    ]

    t = Table(data, colWidths=[120, 380])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Tanda Tangan / Footer Table
    footer_data = [
        [
            Paragraph(f"<b>Tanggal:</b> {tanggal.strftime('%d %B %Y')}", normal_style),
            Paragraph(f"<b>Penerima,</b><br/><br/><br/><u>({penerima})</u>", ParagraphStyle('Center', parent=normal_style, alignment=1))
        ]
    ]
    t_footer = Table(footer_data, colWidths=[300, 200])
    elements.append(t_footer)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- DOWNLOAD BUTTON ---
if submitted:
    pdf_buffer = generate_pdf()
    st.success("Kwitansi berhasil diproses! Klik tombol di bawah untuk mengunduh.")
    st.download_button(
        label="📥 Download Kwitansi PDF",
        data=pdf_buffer,
        file_name=f"Kwitansi_{no_kwitansi}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
