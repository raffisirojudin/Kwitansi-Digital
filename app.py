import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from datetime import date

st.set_page_config(page_title="Digital Receipt Generator", page_icon="🧾", layout="wide")

st.title("🧾 Digital Receipt Generator (Multi-Item)")
st.caption("Generator kwitansi dengan rincian barang dinamis & kalkulator subtotal otomatis.")

# --- FORM INPUT METADATA ---
col_info1, col_info2 = st.columns(2)
with col_info1:
    nama_perusahaan = st.text_input("Nama Usaha / Toko", "PT TECH INDO SEJAHTERA")
    no_kwitansi = st.text_input("No. Kwitansi", "KW-2026/08/001")
    terima_dari = st.text_input("Telah Terima Dari", "PT Maju Bersama")
    tanggal = st.date_input("Tanggal Transaksi", date.today())

with col_info2:
    kota = st.text_input("Kota Transaksi", "Bekasi")
    penerima = st.text_input("Nama Penerima", "Budi Santoso")
    terbilang = st.text_input("Terbilang (Manual/Opsional)", "Tiga Ratus Ribu Rupiah")

st.subheader("📦 Rincian Barang / Layanan")
st.caption("Ubah nilai Qty/Harga atau klik '+' di bawah tabel untuk menambah baris baru.")

# --- DATA DEFAULT ---
default_data = pd.DataFrame([
    {"Nama Barang": "Laptop Asus Zenbook", "Qty": 1, "Harga Satuan": 100000},
    {"Nama Barang": "Mouse Wireless Logitech", "Qty": 2, "Harga Satuan": 100000},
])
default_data["Subtotal"] = default_data["Qty"] * default_data["Harga Satuan"]

# --- TABEL INPUT INTERAKTIF ---
edited_df = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Nama Barang": st.column_config.TextColumn("Nama Barang / Deskripsi", required=True),
        "Qty": st.column_config.NumberColumn("Qty", min_value=1, default=1, step=1),
        "Harga Satuan": st.column_config.NumberColumn("Harga Satuan (Rp)", min_value=0, format="Rp %d"),
        "Subtotal": st.column_config.NumberColumn("Subtotal (Rp)", format="Rp %d", disabled=True),
    }
)

# --- REKALKULASI OTOMATIS ---
edited_df["Subtotal"] = edited_df["Qty"] * edited_df["Harga Satuan"]
total_nominal = edited_df["Subtotal"].sum()

# Display Total Akhir
st.metric("Total Pembayaran Otomatis", f"Rp {total_nominal:,.0f}".replace(",", "."))

btn_generate = st.button("🔨 Generate PDF Kwitansi Multi-Item", type="primary", use_container_width=True)


# --- FUNCTION GENERATE PDF (REPORTLAB) ---
def generate_pdf(df_items, total_val):
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A5),
        rightMargin=25, leftMargin=25, topMargin=20, bottomMargin=20
    )
    
    COLOR_PRIMARY = colors.HexColor('#1E3A8A')
    COLOR_SECONDARY = colors.HexColor('#3B82F6')
    COLOR_TEXT = colors.HexColor('#0F172A')
    COLOR_MUTED = colors.HexColor('#64748B')
    COLOR_BG_LIGHT = colors.HexColor('#F8FAFC')
    COLOR_BORDER = colors.HexColor('#CBD5E1')

    styles = getSampleStyleSheet()
    
    style_comp_title = ParagraphStyle('CompTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, textColor=COLOR_PRIMARY)
    style_comp_sub = ParagraphStyle('CompSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, textColor=COLOR_MUTED)
    style_doc_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=2, textColor=COLOR_TEXT)
    style_doc_no = ParagraphStyle('DocNo', parent=styles['Normal'], fontName='Courier-Bold', fontSize=8.5, alignment=2, textColor=COLOR_SECONDARY)
    
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=COLOR_MUTED)
    style_value_bold = ParagraphStyle('ValueBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, textColor=COLOR_TEXT)
    style_terbilang = ParagraphStyle('Terbilang', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8.5, textColor=COLOR_PRIMARY)
    
    style_tbl_header = ParagraphStyle('TblHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)
    style_tbl_cell = ParagraphStyle('TblCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT)
    style_tbl_cell_right = ParagraphStyle('TblCellR', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=2, textColor=COLOR_TEXT)
    style_tbl_cell_bold_r = ParagraphStyle('TblCellBR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, alignment=2, textColor=COLOR_PRIMARY)

    style_date = ParagraphStyle('DateText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=COLOR_MUTED)
    style_sign_lbl = ParagraphStyle('SignLbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=1, textColor=COLOR_MUTED)
    style_sign_name = ParagraphStyle('SignName', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, alignment=1, textColor=COLOR_TEXT)

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
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(t_header)
    elements.append(Spacer(1, 6))

    # Divider Line
    t_divider = Table([['']], colWidths=[510], rowHeights=[2])
    t_divider.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), COLOR_PRIMARY)]))
    elements.append(t_divider)
    elements.append(Spacer(1, 6))

    # 2. METADATA
    meta_data = [
        [
            Paragraph("Telah Terima Dari", style_label),
            Paragraph(":", style_label),
            Paragraph(f"{terima_dari}", style_value_bold)
        ],
        [
            Paragraph("Uang Sejumlah", style_label),
            Paragraph(":", style_label),
            Paragraph(f"<i>\" {terbilang} \"</i>", style_terbilang)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[110, 10, 390])
    t_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 8))

    # 3. TABEL DINAMIS RINCIAN BARANG
    table_items_data = [
        [
            Paragraph("No", style_tbl_header),
            Paragraph("Nama Barang / Deskripsi", style_tbl_header),
            Paragraph("Qty", style_tbl_header),
            Paragraph("Harga Satuan", style_tbl_header),
            Paragraph("Subtotal", style_tbl_header)
        ]
    ]

    for idx, row in df_items.iterrows():
        harga_fmt = f"Rp {row['Harga Satuan']:,.0f}".replace(",", ".")
        subtotal_fmt = f"Rp {row['Subtotal']:,.0f}".replace(",", ".")
        table_items_data.append([
            Paragraph(str(idx + 1), style_tbl_cell),
            Paragraph(str(row['Nama Barang']), style_tbl_cell),
            Paragraph(str(row['Qty']), style_tbl_cell_right),
            Paragraph(harga_fmt, style_tbl_cell_right),
            Paragraph(subtotal_fmt, style_tbl_cell_right)
        ])

    # Row Total Bayar
    total_fmt = f"Rp {total_val:,.0f}".replace(",", ".")
    table_items_data.append([
        Paragraph("<b>TOTAL BAYAR</b>", style_tbl_cell_bold_r),
        "", "", "",
        Paragraph(f"<b>{total_fmt}</b>", style_tbl_cell_bold_r)
    ])

    t_items = Table(table_items_data, colWidths=[30, 230, 40, 105, 105])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-2), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('SPAN', (0, -1), (3, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), COLOR_BG_LIGHT),
        ('BOX', (0, -1), (-1, -1), 1, COLOR_PRIMARY),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 10))

    # 4. FOOTER TANDA TANGAN
    footer_right = [
        [Paragraph(f"{kota}, {tanggal.strftime('%d %B %Y')}", style_date)],
        [Spacer(1, 2)],
        [Paragraph("Penerima / Bendahara,", style_sign_lbl)],
        [Spacer(1, 28)],
        [Paragraph(f"<u>( {penerima} )</u>", style_sign_name)]
    ]
    t_footer_right = Table(footer_right, colWidths=[180])
    t_footer_right.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))

    t_footer = Table([['', t_footer_right]], colWidths=[330, 180])
    t_footer.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT')]))
    elements.append(t_footer)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# --- TOMBOL GENERATE & DOWNLOAD ---
if btn_generate:
    if edited_df.empty or total_nominal == 0:
        st.error("Daftar barang tidak boleh kosong!")
    else:
        pdf_buf = generate_pdf(edited_df, total_nominal)
        st.success("Kwitansi PDF berhasil dibuat!")
        st.download_button(
            label="📥 Download Kwitansi PDF",
            data=pdf_buf,
            file_name=f"Kwitansi_{no_kwitansi}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
