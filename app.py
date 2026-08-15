import streamlit as st
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from datetime import date

st.set_page_config(page_title="Digital Receipt Generator", page_icon="🧾", layout="centered")

st.title("🧾 Digital Receipt Generator")
st.caption("Generator kwitansi digital dengan desain modern & profesional.")

# --- FORM INPUT ---
with st.form("receipt_form"):
    col1, col2 = st.columns(2)
    with col1:
        nama_perusahaan = st.text_input("Nama Usaha / Toko", "PT TECH INDO SEJAHTERA")
        no_kwitansi = st.text_input("No. Kwitansi", "KW-2026/08/001")
        terima_dari = st.text_input("Telah Terima Dari", "PT Maju Bersama")
        tanggal = st.date_input("Tanggal Transaksi", date.today())
    with col2:
        kota = st.text_input("Kota Transaksi", "Jakarta")
        nominal = st.number_input("Nominal (Rp)", min_value=0, value=1500000, step=50000)
        terbilang = st.text_input("Terbilang", "Satu Juta Lima Ratus Ribu Rupiah")
        penerima = st.text_input("Nama Penerima", "Budi Santoso")
        
    keperluan = st.text_area("Untuk Pembayaran", "Pembelian 1 Unit Laptop Asus & Lisensi Software Kustomasi Sistem")
    
    submitted = st.form_submit_button("🔨 Generate PDF Kwitansi Modern")


# --- PDF GENERATOR (REVISED PROFESSIONAL DESIGN) ---
def generate_pdf():
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A5),
        rightMargin=25, leftMargin=25, topMargin=20, bottomMargin=20
    )
    
    COLOR_PRIMARY = colors.HexColor('#1E3A8A')   # Navy Blue
    COLOR_SECONDARY = colors.HexColor('#3B82F6') # Accent Blue
    COLOR_TEXT = colors.HexColor('#0F172A')      # Dark Slate
    COLOR_MUTED = colors.HexColor('#64748B')     # Muted Grey
    COLOR_BG_BOX = colors.HexColor('#F8FAFC')    # Light Slate Fill
    COLOR_BORDER = colors.HexColor('#CBD5E1')    # Light Border

    styles = getSampleStyleSheet()
    
    style_comp_title = ParagraphStyle('CompTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=COLOR_PRIMARY)
    style_comp_sub = ParagraphStyle('CompSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=COLOR_MUTED)
    
    style_doc_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=17, alignment=2, textColor=COLOR_TEXT)
    style_doc_no = ParagraphStyle('DocNo', parent=styles['Normal'], fontName='Courier-Bold', fontSize=9, leading=11, alignment=2, textColor=COLOR_SECONDARY)
    
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=COLOR_MUTED)
    style_value = ParagraphStyle('Value', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=COLOR_TEXT)
    style_value_bold = ParagraphStyle('ValueBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=COLOR_TEXT)
    style_terbilang = ParagraphStyle('Terbilang', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=12, textColor=COLOR_PRIMARY)
    style_amount_val = ParagraphStyle('AmtVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=COLOR_PRIMARY)
    
    style_date = ParagraphStyle('DateText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=COLOR_MUTED)
    style_sign_lbl = ParagraphStyle('SignLbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, alignment=1, textColor=COLOR_MUTED)
    style_sign_name = ParagraphStyle('SignName', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, alignment=1, textColor=COLOR_TEXT)

    elements = []

    # 1. HEADER
    header_data = [
        [
            Paragraph(f"<b>{nama_perusahaan.upper()}</b>", style_comp_title),
            Paragraph("<b>KWITANSI PEMBAYARAN</b>", style_doc_title)
        ],
        [
            Paragraph("BUKTI PEMBAYARAN RESMI DIGITAL", style_comp_sub),
            Paragraph(f"NO: {no_kwitansi}", style_doc_no)
        ]
    ]
    t_header = Table(header_data, colWidths=[270, 240])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 8))

    # Divider Line
    t_divider = Table([['']], colWidths=[510], rowHeights=[2])
    t_divider.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PRIMARY),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(t_divider)
    elements.append(Spacer(1, 10))

    # 2. CONTENT TABLE (Termasuk Jumlah Rp Sejajar)
    formatted_nominal = f"Rp {nominal:,.0f}".replace(",", ".")
    content_data = [
        [
            Paragraph("Telah Terima Dari", style_label),
            Paragraph(":", style_label),
            Paragraph(f"{terima_dari}", style_value_bold)
        ],
        [
            Paragraph("Uang Sejumlah", style_label),
            Paragraph(":", style_label),
            Paragraph(f"<i>\" {terbilang} \"</i>", style_terbilang)
        ],
        [
            Paragraph("Untuk Pembayaran", style_label),
            Paragraph(":", style_label),
            Paragraph(f"{keperluan}", style_value)
        ],
        [
            Paragraph("Jumlah Rp", style_label),
            Paragraph(":", style_label),
            Paragraph(f"<b>{formatted_nominal}</b>", style_amount_val)
        ]
    ]
    t_content = Table(content_data, colWidths=[120, 15, 375])
    t_content.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        # Terbilang Box Fill
        ('BACKGROUND', (2,1), (2,1), COLOR_BG_BOX),
        ('BOX', (2,1), (2,1), 0.5, COLOR_BORDER),
        ('LEFTPADDING', (2,1), (2,1), 8),
        ('RIGHTPADDING', (2,1), (2,1), 8),
        # Nominal Box Accent Fill (Elegan & Sejajar)
        ('BACKGROUND', (2,3), (2,3), COLOR_BG_BOX),
        ('BOX', (2,3), (2,3), 1, COLOR_PRIMARY),
        ('LEFTPADDING', (2,3), (2,3), 10),
        ('RIGHTPADDING', (2,3), (2,3), 10),
        ('TOPPADDING', (2,3), (2,3), 6),
        ('BOTTOMPADDING', (2,3), (2,3), 6),
    ]))
    elements.append(t_content)
    elements.append(Spacer(1, 15))

    # 3. FOOTER (Tanggal & Tanda Tangan)
    footer_right = [
        [Paragraph(f"{kota}, {tanggal.strftime('%d %B %Y')}", style_date)],
        [Spacer(1, 4)],
        [Paragraph("Penerima / Bendahara,", style_sign_lbl)],
        [Spacer(1, 35)],
        [Paragraph(f"<u>( {penerima} )</u>", style_sign_name)]
    ]
    t_footer_right = Table(footer_right, colWidths=[200])
    t_footer_right.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    t_footer = Table([['', t_footer_right]], colWidths=[310, 200])
    t_footer.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(t_footer)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- DOWNLOAD BUTTON ---
if submitted:
    pdf_buffer = generate_pdf()
    st.success("Kwitansi berhasil direvisi!")
    st.download_button(
        label="📥 Download Kwitansi PDF (Revisi Modern)",
        data=pdf_buffer,
        file_name=f"Kwitansi_{no_kwitansi}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
