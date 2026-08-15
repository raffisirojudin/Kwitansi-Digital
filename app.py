import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4, A5, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
import io
from datetime import date
from PIL import Image
from pdf2image import convert_from_bytes

st.set_page_config(page_title="Digital Receipt Generator Pro", page_icon="🧾", layout="wide")

st.title("🧾 Digital Receipt Generator Pro")
st.caption("Generator kwitansi multi-item dengan pilihan ukuran kertas (A4, A5, Struk 80mm), custom warna, logo, dan info penjual.")

# --- SIDEBAR: KERTAS, DESAIN & BRANDING ---
st.sidebar.header("📐 Ukuran & Orientasi Kertas")

# Konfigurasi Dimensi & Skala Kertas
PAPER_CONFIGS = {
    "A5 Landscape (Default)": {
        "pagesize": landscape(A5), "margin": 25,
        "tbl_widths": [30, 245, 40, 110, 110],
        "scale": 1.0, "preview_max_width": "100%", "preview_font_size": "13px"
    },
    "A5 Portrait": {
        "pagesize": A5, "margin": 20,
        "tbl_widths": [25, 175, 30, 70, 70],
        "scale": 0.85, "preview_max_width": "550px", "preview_font_size": "12px"
    },
    "A4 Landscape": {
        "pagesize": landscape(A4), "margin": 30,
        "tbl_widths": [40, 420, 50, 135, 135],
        "scale": 1.15, "preview_max_width": "100%", "preview_font_size": "14px"
    },
    "A4 Portrait": {
        "pagesize": A4, "margin": 25,
        "tbl_widths": [30, 255, 40, 110, 110],
        "scale": 1.0, "preview_max_width": "750px", "preview_font_size": "13px"
    },
    "Struk Kasir (80mm Thermal)": {
        "pagesize": (80 * mm, 220 * mm), "margin": 6,
        "tbl_widths": [14, 80, 20, 50, 50],
        "scale": 0.65, "preview_max_width": "340px", "preview_font_size": "10px"
    }
}

selected_paper_name = st.sidebar.selectbox("Pilih Ukuran Kertas", list(PAPER_CONFIGS.keys()))
paper_cfg = PAPER_CONFIGS[selected_paper_name]

st.sidebar.header("🎨 Desain & Branding")
uploaded_logo = st.sidebar.file_uploader("Unggah Logo Toko/Usaha", type=["png", "jpg", "jpeg"])

COLOR_PRESETS = {
    "Classic Blue": {"primary": "#1E3A8A", "secondary": "#3B82F6", "bg_light": "#F8FAFC"},
    "Forest Green": {"primary": "#064E3B", "secondary": "#10B981", "bg_light": "#F0FDF4"},
    "Elegant Charcoal": {"primary": "#18181B", "secondary": "#71717A", "bg_light": "#FAFAFA"},
    "Crimson Red": {"primary": "#881337", "secondary": "#F43F5E", "bg_light": "#FFF1F2"}
}

selected_theme_name = st.sidebar.selectbox("Pilihan Warna Kwitansi", list(COLOR_PRESETS.keys()))
theme = COLOR_PRESETS[selected_theme_name]

# --- FORM INPUT METADATA ---
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown("### 🏢 Informasi Penjual / Toko")
    nama_perusahaan = st.text_input("Nama Usaha / Toko", "PT TECH INDO SEJAHTERA")
    alamat_perusahaan = st.text_input("Alamat Toko", "Jl. Jend. Sudirman No. 45, Jakarta Pusat")
    telepon_perusahaan = st.text_input("No. Telp / WhatsApp", "0812-3456-7890")
    
    st.markdown("### 📝 Detail Transaksi")
    no_kwitansi = st.text_input("No. Kwitansi", "KW-2026/08/001")
    terima_dari = st.text_input("Telah Terima Dari", "PT Maju Bersama")

with col_info2:
    st.markdown("### 📍 Lokasi & Tanggal")
    kota = st.text_input("Kota Transaksi", "Bekasi")
    tanggal = st.date_input("Tanggal Transaksi", date.today())
    penerima = st.text_input("Nama Penerima / Kasir", "Budi Santoso")
    terbilang = st.text_input("Terbilang (Manual/Opsional)", "Tiga Ratus Ribu Rupiah")
    
    st.markdown("### 💳 Info Rekening / Catatan Pembayaran")
    catatan_pembayaran = st.text_area(
        "No. Rekening & Catatan Tambahan",
        "Pembayaran via Transfer:\nBCA: 1234-567-890 a.n PT Tech Indo\nMandiri: 9876-543-210 a.n PT Tech Indo",
        height=90
    )

st.subheader("📦 Rincian Barang / Layanan")

default_data = pd.DataFrame([
    {"Nama Barang": "Laptop Asus Zenbook", "Qty": 1, "Harga Satuan": 100000},
    {"Nama Barang": "Mouse Wireless Logitech", "Qty": 2, "Harga Satuan": 100000},
])

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

# Rekalkulasi Otomatis (Aman Tipe Data)
edited_df["Qty"] = pd.to_numeric(edited_df["Qty"], errors='coerce').fillna(0).astype(int)
edited_df["Harga Satuan"] = pd.to_numeric(edited_df["Harga Satuan"], errors='coerce').fillna(0).astype(float)
edited_df["Subtotal"] = edited_df["Qty"] * edited_df["Harga Satuan"]
total_nominal = float(edited_df["Subtotal"].sum())

st.metric("Total Pembayaran Otomatis", f"Rp {total_nominal:,.0f}".replace(",", "."))

# --- HELPER FUNCTIONS FOR EXPORT ---

def generate_excel(df_items, total_val):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_items.to_excel(writer, sheet_name='Kwitansi', index=False, startrow=8)
        workbook  = writer.book
        worksheet = writer.sheets['Kwitansi']
        
        fmt_title = workbook.add_format({'bold': True, 'font_size': 14})
        fmt_sub = workbook.add_format({'font_size': 9, 'color': '#64748B'})
        fmt_header = workbook.add_format({'bold': True, 'bg_color': theme["primary"], 'font_color': 'white'})
        fmt_bold_currency = workbook.add_format({'bold': True, 'num_format': 'Rp #,##0'})

        worksheet.write('A1', nama_perusahaan.upper(), fmt_title)
        worksheet.write('A2', f"Alamat: {alamat_perusahaan} | Telp: {telepon_perusahaan}", fmt_sub)
        worksheet.write('A4', f"No. Kwitansi: {no_kwitansi}")
        worksheet.write('A5', f"Terima Dari: {terima_dari}")
        worksheet.write('A6', f"Tanggal: {tanggal.strftime('%d-%m-%Y')}")
        
        total_row_idx = len(df_items) + 9
        worksheet.write(f'C{total_row_idx}', 'TOTAL BAYAR', fmt_header)
        worksheet.write(f'D{total_row_idx}', f'=SUM(D9:D{total_row_idx-1})', fmt_bold_currency)

        worksheet.write(f'A{total_row_idx+2}', 'Info Pembayaran / Catatan:')
        worksheet.write(f'A{total_row_idx+3}', catatan_pembayaran)
        
    output.seek(0)
    return output

def generate_pdf(df_items, total_val, logo_file, config):
    buffer = io.BytesIO()
    margin = config["margin"]
    doc = SimpleDocTemplate(
        buffer, pagesize=config["pagesize"],
        rightMargin=margin, leftMargin=margin, topMargin=margin, bottomMargin=margin
    )
    
    # Perhitungan lebar printable area
    page_w = config["pagesize"][0]
    printable_w = page_w - (2 * margin)
    s = config["scale"] # Scale Factor

    col_primary = colors.HexColor(theme["primary"])
    col_secondary = colors.HexColor(theme["secondary"])
    col_bg_light = colors.HexColor(theme["bg_light"])
    col_text = colors.HexColor('#0F172A')
    col_muted = colors.HexColor('#64748B')
    col_border = colors.HexColor('#CBD5E1')

    styles = getSampleStyleSheet()
    style_comp_title = ParagraphStyle('CompTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11*s, leading=13*s, textColor=col_primary)
    style_comp_sub = ParagraphStyle('CompSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=6.5*s, leading=8*s, textColor=col_muted)
    style_comp_addr = ParagraphStyle('CompAddr', parent=styles['Normal'], fontName='Helvetica', fontSize=6.5*s, leading=8*s, textColor=col_muted)
    
    style_doc_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12*s, leading=14*s, alignment=2, textColor=col_text)
    style_doc_no = ParagraphStyle('DocNo', parent=styles['Normal'], fontName='Courier-Bold', fontSize=8*s, leading=10*s, alignment=2, textColor=col_secondary)
    
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8*s, leading=10*s, textColor=col_muted)
    style_value_bold = ParagraphStyle('ValueBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5*s, leading=11*s, textColor=col_text)
    style_terbilang = ParagraphStyle('Terbilang', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8*s, leading=10*s, textColor=col_primary)
    
    style_tbl_header = ParagraphStyle('TblHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8*s, leading=10*s, textColor=colors.white)
    style_tbl_cell = ParagraphStyle('TblCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8*s, leading=10*s, textColor=col_text)
    style_tbl_cell_right = ParagraphStyle('TblCellR', parent=styles['Normal'], fontName='Helvetica', fontSize=8*s, leading=10*s, alignment=2, textColor=col_text)
    style_tbl_cell_bold_r = ParagraphStyle('TblCellBR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5*s, leading=11*s, alignment=2, textColor=col_primary)

    style_note_hdr = ParagraphStyle('NoteHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5*s, leading=9*s, textColor=col_primary)
    style_note_body = ParagraphStyle('NoteBody', parent=styles['Normal'], fontName='Helvetica', fontSize=7*s, leading=9*s, textColor=col_muted)

    style_date = ParagraphStyle('DateText', parent=styles['Normal'], fontName='Helvetica', fontSize=8*s, leading=10*s, textColor=col_muted)
    style_sign_lbl = ParagraphStyle('SignLbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8*s, leading=10*s, alignment=1, textColor=col_muted)
    style_sign_name = ParagraphStyle('SignName', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5*s, leading=11*s, alignment=1, textColor=col_text)

    elements = []

    # 1. Header dengan Info Penjual & Logo
    w_head_left = printable_w * 0.55
    w_head_right = printable_w * 0.45

    company_cell = [
        Paragraph(f"<b>{nama_perusahaan.upper()}</b>", style_comp_title),
        Paragraph(f"{alamat_perusahaan} | Telp: {telepon_perusahaan}", style_comp_addr),
        Paragraph("BUKTI PEMBAYARAN RESMI DIGITAL", style_comp_sub)
    ]
    
    if logo_file:
        img_w = 35 * s
        img_data = io.BytesIO(logo_file.getvalue())
        rl_img = RLImage(img_data, width=img_w, height=img_w)
        rl_img.hAlign = 'LEFT'
        header_left = Table([[rl_img, company_cell]], colWidths=[img_w + 5, w_head_left - (img_w + 5)])
        header_left.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0)
        ]))
    else:
        header_left = company_cell

    header_data = [
        [header_left, Paragraph("<b>KWITANSI PEMBAYARAN</b>", style_doc_title)],
        ["", Paragraph(f"NO: {no_kwitansi}", style_doc_no)]
    ]
    
    t_header = Table(header_data, colWidths=[w_head_left, w_head_right])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 4 * s))

    # 2. Pembatas
    t_divider = Table([['']], colWidths=[printable_w], rowHeights=[2 * s])
    t_divider.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), col_primary)]))
    elements.append(t_divider)
    elements.append(Spacer(1, 4 * s))

    # 3. Metadata
    w_meta1 = printable_w * 0.20
    w_meta2 = printable_w * 0.03
    w_meta3 = printable_w * 0.77
    meta_data = [
        [Paragraph("Telah Terima Dari", style_label), Paragraph(":", style_label), Paragraph(f"{terima_dari}", style_value_bold)],
        [Paragraph("Uang Sejumlah", style_label), Paragraph(":", style_label), Paragraph(f"<i>\" {terbilang} \"</i>", style_terbilang)]
    ]
    t_meta = Table(meta_data, colWidths=[w_meta1, w_meta2, w_meta3])
    t_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 1),
        ('RIGHTPADDING', (0,0), (-1,-1), 1),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 6 * s))

    # 4. Tabel Rincian Barang (Dinamis Sesuai Ukuran Kertas)
    table_items_data = [[
        Paragraph("No", style_tbl_header), Paragraph("Nama Barang / Deskripsi", style_tbl_header),
        Paragraph("Qty", style_tbl_header), Paragraph("Harga Satuan", style_tbl_header), Paragraph("Subtotal", style_tbl_header)
    ]]

    for idx, row in df_items.iterrows():
        qty_val = int(row['Qty'])
        harga_val = float(row['Harga Satuan'])
        subtotal_val = float(row['Subtotal'])

        harga_fmt = f"Rp {harga_val:,.0f}".replace(",", ".")
        subtotal_fmt = f"Rp {subtotal_val:,.0f}".replace(",", ".")

        table_items_data.append([
            Paragraph(str(idx + 1), style_tbl_cell),
            Paragraph(str(row['Nama Barang']), style_tbl_cell),
            Paragraph(str(qty_val), style_tbl_cell_right),
            Paragraph(harga_fmt, style_tbl_cell_right),
            Paragraph(subtotal_fmt, style_tbl_cell_right)
        ])

    table_items_data.append([
        Paragraph("<b>TOTAL BAYAR</b>", style_tbl_cell_bold_r), "", "", "",
        Paragraph(f"<b>Rp {total_val:,.0f}</b>".replace(",", "."), style_tbl_cell_bold_r)
    ])

    t_items = Table(table_items_data, colWidths=config["tbl_widths"])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), col_primary),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-2), 0.5, col_border),
        ('LEFTPADDING', (0,0), (-1,-1), 3 * s),
        ('RIGHTPADDING', (0,0), (-1,-1), 3 * s),
        ('SPAN', (0, -1), (3, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), col_bg_light),
        ('BOX', (0, -1), (-1, -1), 1, col_primary),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 6 * s))

    # 5. Footer (Catatan & Tanda Tangan)
    w_foot_left = printable_w * 0.62
    w_foot_right = printable_w * 0.38

    formatted_catatan = catatan_pembayaran.replace('\n', '<br/>')
    footer_left = [
        [Paragraph("<b>Informasi Pembayaran / Catatan:</b>", style_note_hdr)],
        [Paragraph(formatted_catatan, style_note_body)]
    ]
    t_footer_left = Table(footer_left, colWidths=[w_foot_left])
    t_footer_left.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))

    footer_right = [
        [Paragraph(f"{kota}, {tanggal.strftime('%d %B %Y')}", style_date)],
        [Spacer(1, 2 * s)],
        [Paragraph("Penerima / Bendahara,", style_sign_lbl)],
        [Spacer(1, 16 * s)],
        [Paragraph(f"<u>( {penerima} )</u>", style_sign_name)]
    ]
    t_footer_right = Table(footer_right, colWidths=[w_foot_right])
    t_footer_right.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))

    t_footer = Table([[t_footer_left, t_footer_right]], colWidths=[w_foot_left, w_foot_right])
    t_footer.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(t_footer)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_png_from_pdf(pdf_buffer):
    images = convert_from_bytes(pdf_buffer.getvalue())
    img_byte_arr = io.BytesIO()
    if images:
        images[0].save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
    return img_byte_arr

# --- PANEL EXPORT MULTI-FORMAT ---
st.subheader("📥 Export & Download Kwitansi")

pdf_buf = generate_pdf(edited_df, total_nominal, uploaded_logo, paper_cfg)

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    st.markdown("##### 📄 Format PDF (Cetak)")
    st.download_button(
        label=f"Download PDF ({selected_paper_name.split()[0]})",
        data=pdf_buf,
        file_name=f"Kwitansi_{no_kwitansi}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with col_exp2:
    st.markdown("##### 🖼️ Format PNG (Gambar/WA)")
    try:
        png_buf = generate_png_from_pdf(pdf_buf)
        st.download_button(
            label="Download PNG",
            data=png_buf,
            file_name=f"Kwitansi_{no_kwitansi}.png",
            mime="image/png",
            use_container_width=True
        )
    except Exception:
        st.warning("Gunakan PDF atau pasang poppler-utils untuk konversi PNG.")

with col_exp3:
    st.markdown("##### 📊 Format Excel (Rekap)")
    excel_buf = generate_excel(edited_df, total_nominal)
    st.download_button(
        label="Download Excel",
        data=excel_buf,
        file_name=f"Rekap_Kwitansi_{no_kwitansi}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# --- PREVIEW KWITANSI DIGITAL (SKALA DINAMIS) ---
st.divider()
st.subheader(f"👁️ Live Preview Kwitansi Digital ({selected_paper_name})")

items_html = ""
for idx, row in edited_df.iterrows():
    qty_v = int(row['Qty'])
    h_v = float(row['Harga Satuan'])
    s_v = float(row['Subtotal'])
    
    h_fmt = f"Rp {h_v:,.0f}".replace(",", ".")
    s_fmt = f"Rp {s_v:,.0f}".replace(",", ".")
    items_html += f"<tr><td style='padding:4px;border-bottom:1px solid #E2E8F0;'>{idx+1}</td><td style='padding:4px;border-bottom:1px solid #E2E8F0;'>{row['Nama Barang']}</td><td style='padding:4px;border-bottom:1px solid #E2E8F0;text-align:right;'>{qty_v}</td><td style='padding:4px;border-bottom:1px solid #E2E8F0;text-align:right;'>{h_fmt}</td><td style='padding:4px;border-bottom:1px solid #E2E8F0;text-align:right;'>{s_fmt}</td></tr>"

tot_fmt = f"Rp {total_nominal:,.0f}".replace(",", ".")
html_catatan = catatan_pembayaran.replace('\n', '<br/>')

preview_html = f"""<div style="max-width:{paper_cfg['preview_max_width']};margin:0 auto;border:2px solid {theme['primary']};border-radius:8px;padding:15px;background-color:#FFFFFF;color:#0F172A;font-family:sans-serif;font-size:{paper_cfg['preview_font_size']};">
<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid {theme['primary']};padding-bottom:8px;">
<div>
    <h3 style="margin:0;color:{theme['primary']};">{nama_perusahaan.upper()}</h3>
    <div style="font-size:0.85em;color:#64748B;">{alamat_perusahaan} | Telp: {telepon_perusahaan}</div>
    <small style="color:#64748B;">BUKTI PEMBAYARAN RESMI DIGITAL</small>
</div>
<div style="text-align:right;"><h4 style="margin:0;color:#0F172A;">KWITANSI PEMBAYARAN</h4><span style="color:{theme['secondary']};font-family:monospace;font-size:0.9em;">NO: {no_kwitansi}</span></div>
</div>
<div style="margin:10px 0;">
<p style="margin:2px 0;"><strong>Telah Terima Dari:</strong> {terima_dari}</p>
<p style="margin:2px 0;color:{theme['primary']};"><strong>Uang Sejumlah:</strong> <i>"{terbilang}"</i></p>
</div>
<table style="width:100%;border-collapse:collapse;margin-top:8px;">
<thead><tr style="background-color:{theme['primary']};color:white;text-align:left;"><th style="padding:4px;">No</th><th style="padding:4px;">Nama Barang / Deskripsi</th><th style="padding:4px;text-align:right;">Qty</th><th style="padding:4px;text-align:right;">Harga Satuan</th><th style="padding:4px;text-align:right;">Subtotal</th></tr></thead>
<tbody>
{items_html}
<tr style="background-color:{theme['bg_light']};font-weight:bold;color:{theme['primary']};"><td colspan="4" style="padding:6px;text-align:right;">TOTAL BAYAR</td><td style="padding:6px;text-align:right;">{tot_fmt}</td></tr>
</tbody>
</table>
<div style="display:flex;justify-content:space-between;margin-top:15px;gap:10px;">
<div style="max-width:55%;color:#64748B;font-size:0.85em;">
    <strong style="color:{theme['primary']};">Informasi Pembayaran / Catatan:</strong><br/>
    <span>{html_catatan}</span>
</div>
<div style="text-align:right;color:#64748B;font-size:0.85em;">
    <p style="margin:0;">{kota}, {tanggal.strftime('%d %B %Y')}</p>
    <p style="margin:0;">Penerima / Bendahara,</p>
    <br><br>
    <p style="margin:0;font-weight:bold;color:#0F172A;"><u>( {penerima} )</u></p>
</div>
</div>
</div>"""

st.components.v1.html(preview_html, height=520, scrolling=True)
