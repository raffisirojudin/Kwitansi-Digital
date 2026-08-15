import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from datetime import date
from PIL import Image

st.set_page_config(page_title="Digital Receipt Generator Pro", page_icon="🧾", layout="wide")

st.title("🧾 Digital Receipt Generator Pro")
st.caption("Generator kwitansi multi-item dengan custom warna, logo, dan export PDF/Excel/PNG.")

# --- SIDEBAR: CUSTOMISASI TEMA & LOGO ---
st.sidebar.header("🎨 Desain & Branding")

# 1. Custom Logo
uploaded_logo = st.sidebar.file_uploader("Unggah Logo Toko/Usaha", type=["png", "jpg", "jpeg"])

# 2. Custom Warna Kwitansi
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
    nama_perusahaan = st.text_input("Nama Usaha / Toko", "PT TECH INDO SEJAHTERA")
    no_kwitansi = st.text_input("No. Kwitansi", "KW-2026/08/001")
    terima_dari = st.text_input("Telah Terima Dari", "PT Maju Bersama")
    tanggal = st.date_input("Tanggal Transaksi", date.today())

with col_info2:
    kota = st.text_input("Kota Transaksi", "Bekasi")
    penerima = st.text_input("Nama Penerima", "Budi Santoso")
    terbilang = st.text_input("Terbilang (Manual/Opsional)", "Tiga Ratus Ribu Rupiah")

st.subheader("📦 Rincian Barang / Layanan")

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

# Rekalkulasi Otomatis
edited_df["Subtotal"] = edited_df["Qty"] * edited_df["Harga Satuan"]
total_nominal = edited_df["Subtotal"].sum()

st.metric("Total Pembayaran Otomatis", f"Rp {total_nominal:,.0f}".replace(",", "."))


# --- HELPER FUNCTIONS FOR EXPORT ---

# 1. GENERATE EXCEL (.xlsx)
def generate_excel(df_items, total_val):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet Data Utama
        df_items.to_excel(writer, sheet_name='Kwitansi', index=False, startrow=6)
        
        workbook  = writer.book
        worksheet = writer.sheets['Kwitansi']
        
        # Formatting Excel
        fmt_title = workbook.add_format({'bold': True, 'font_size': 14})
        fmt_header = workbook.add_format({'bold': True, 'bg_color': theme["primary"], 'font_color': 'white'})
        fmt_currency = workbook.add_format({'num_format': 'Rp #,##0'})
        fmt_bold_currency = workbook.add_format({'bold': True, 'num_format': 'Rp #,##0'})

        # Header Metadata
        worksheet.write('A1', nama_perusahaan.upper(), fmt_title)
        worksheet.write('A2', f"No. Kwitansi: {no_kwitansi}")
        worksheet.write('A3', f"Terima Dari: {terima_dari}")
        worksheet.write('A4', f"Tanggal: {tanggal.strftime('%d-%m-%Y')}")
        
        # Total Bayar Row
        total_row_idx = len(df_items) + 7
        worksheet.write(f'C{total_row_idx}', 'TOTAL BAYAR', fmt_header)
        worksheet.write(f'D{total_row_idx}', f'=SUM(D7:D{total_row_idx-1})', fmt_bold_currency)
        
    output.seek(0)
    return output


# 2. GENERATE PDF (ReportLab) WITH LOGO & CUSTOM COLOR
def generate_pdf(df_items, total_val, logo_file):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A5),
        rightMargin=25, leftMargin=25, topMargin=15, bottomMargin=15
    )
    
    col_primary = colors.HexColor(theme["primary"])
    col_secondary = colors.HexColor(theme["secondary"])
    col_bg_light = colors.HexColor(theme["bg_light"])
    col_text = colors.HexColor('#0F172A')
    col_muted = colors.HexColor('#64748B')
    col_border = colors.HexColor('#CBD5E1')

    styles = getSampleStyleSheet()
    style_comp_title = ParagraphStyle('CompTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=col_primary)
    style_comp_sub = ParagraphStyle('CompSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=col_muted)
    style_doc_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=15, alignment=2, textColor=col_text)
    style_doc_no = ParagraphStyle('DocNo', parent=styles['Normal'], fontName='Courier-Bold', fontSize=8.5, leading=10, alignment=2, textColor=col_secondary)
    
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=col_muted)
    style_value_bold = ParagraphStyle('ValueBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=col_text)
    style_terbilang = ParagraphStyle('Terbilang', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=col_primary)
    
    style_tbl_header = ParagraphStyle('TblHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    style_tbl_cell = ParagraphStyle('TblCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=col_text)
    style_tbl_cell_right = ParagraphStyle('TblCellR', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=2, textColor=col_text)
    style_tbl_cell_bold_r = ParagraphStyle('TblCellBR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, alignment=2, textColor=col_primary)

    style_date = ParagraphStyle('DateText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=col_muted)
    style_sign_lbl = ParagraphStyle('SignLbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=1, textColor=col_muted)
    style_sign_name = ParagraphStyle('SignName', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, alignment=1, textColor=col_text)

    elements = []

    # Prepare Header with Optional Logo
    company_cell = [
        Paragraph(f"<b>{nama_perusahaan.upper()}</b>", style_comp_title),
        Paragraph("BUKTI PEMBAYARAN RESMI DIGITAL", style_comp_sub)
    ]
    
    if logo_file:
        img_data = io.BytesIO(logo_file.getvalue())
        rl_img = RLImage(img_data, width=40, height=40)
        rl_img.hAlign = 'LEFT'
        header_left = Table([[rl_img, company_cell]], colWidths=[45, 240])
        header_left.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    else:
        header_left = company_cell

    header_data = [
        [header_left, Paragraph("<b>KWITANSI PEMBAYARAN</b>", style_doc_title)],
        ["", Paragraph(f"NO: {no_kwitansi}", style_doc_no)]
    ]
    
    t_header = Table(header_data, colWidths=[285, 250])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 4))

    # Divider
    t_divider = Table([['']], colWidths=[535], rowHeights=[2])
    t_divider.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), col_primary)]))
    elements.append(t_divider)
    elements.append(Spacer(1, 4))

    # Metadata
    meta_data = [
        [Paragraph("Telah Terima Dari", style_label), Paragraph(":", style_label), Paragraph(f"{terima_dari}", style_value_bold)],
        [Paragraph("Uang Sejumlah", style_label), Paragraph(":", style_label), Paragraph(f"<i>\" {terbilang} \"</i>", style_terbilang)]
    ]
    t_meta = Table(meta_data, colWidths=[100, 10, 425])
    t_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 6))

    # Items Table
    table_items_data = [[
        Paragraph("No", style_tbl_header), Paragraph("Nama Barang / Deskripsi", style_tbl_header),
        Paragraph("Qty", style_tbl_header), Paragraph("Harga Satuan", style_tbl_header), Paragraph("Subtotal", style_tbl_header)
    ]]

    for idx, row in df_items.iterrows():
        table_items_data.append([
            Paragraph(str(idx + 1), style_tbl_cell),
            Paragraph(str(row['Nama Barang']), style_tbl_cell),
            Paragraph(str(row['Qty']), style_tbl_cell_right),
            Paragraph(f"Rp {row['Harga Satuan']:,.0f}".replace(",", "."), style_tbl_cell_right),
            Paragraph(f"Rp {row['Subtotal']:,.0f}".replace(",", "."), style_tbl_cell_right)
        ])

    table_items_data.append([
        Paragraph("<b>TOTAL BAYAR</b>", style_tbl_cell_bold_r), "", "", "",
        Paragraph(f"<b>Rp {total_val:,.0f}</b>".replace(",", "."), style_tbl_cell_bold_r)
    ])

    t_items = Table(table_items_data, colWidths=[30, 245, 40, 110, 110])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), col_primary),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-2), 0.5, col_border),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('SPAN', (0, -1), (3, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), col_bg_light),
        ('BOX', (0, -1), (-1, -1), 1, col_primary),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 6))

    # Footer Sign
    footer_right = [
        [Paragraph(f"{kota}, {tanggal.strftime('%d %B %Y')}", style_date)],
        [Spacer(1, 2)],
        [Paragraph("Penerima / Bendahara,", style_sign_lbl)],
        [Spacer(1, 20)],
        [Paragraph(f"<u>( {penerima} )</u>", style_sign_name)]
    ]
    t_footer_right = Table(footer_right, colWidths=[180])
    t_footer_right.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))

    t_footer = Table([['', t_footer_right]], colWidths=[355, 180])
    t_footer.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT')]))
    elements.append(t_footer)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# --- PANEL EXPORT MULTI-FORMAT ---
st.subheader("📥 Export & Download Kwitansi")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    st.markdown("##### 📄 Format PDF (Siap Cetak)")
    pdf_buf = generate_pdf(edited_df, total_nominal, uploaded_logo)
    st.download_button(
        label="Download Kwitansi PDF",
        data=pdf_buf,
        file_name=f"Kwitansi_{no_kwitansi}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with col_exp2:
    st.markdown("##### 📊 Format Excel (Pembukuan)")
    excel_buf = generate_excel(edited_df, total_nominal)
    st.download_button(
        label="Download Rekap Excel",
        data=excel_buf,
        file_name=f"Rekap_Kwitansi_{no_kwitansi}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# --- PREVIEW KWITANSI (HTML FIX) ---
st.divider()
st.subheader("👁️ Live Preview Kwitansi Digital")

items_html = ""
for idx, row in edited_df.iterrows():
    subtotal_val = row['Qty'] * row['Harga Satuan']
    h_fmt = f"Rp {row['Harga Satuan']:,.0f}".replace(",", ".")
    s_fmt = f"Rp {subtotal_val:,.0f}".replace(",", ".")
    items_html += f"<tr><td style='padding:6px;border-bottom:1px solid #E2E8F0;'>{idx+1}</td><td style='padding:6px;border-bottom:1px solid #E2E8F0;'>{row['Nama Barang']}</td><td style='padding:6px;border-bottom:1px solid #E2E8F0;text-align:right;'>{row['Qty']}</td><td style='padding:6px;border-bottom:1px solid #E2E8F0;text-align:right;'>{h_fmt}</td><td style='padding:6px;border-bottom:1px solid #E2E8F0;text-align:right;'>{s_fmt}</td></tr>"

tot_fmt = f"Rp {total_nominal:,.0f}".replace(",", ".")

# String HTML tanpa indentasi awal agar tidak dianggap codeblock oleh Streamlit
preview_html = f"""<div style="border:2px solid {theme['primary']};border-radius:8px;padding:20px;background-color:#FFFFFF;color:#0F172A;font-family:sans-serif;">
<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid {theme['primary']};padding-bottom:10px;">
<div><h2 style="margin:0;color:{theme['primary']};">{nama_perusahaan.upper()}</h2><small style="color:#64748B;">BUKTI PEMBAYARAN RESMI DIGITAL</small></div>
<div style="text-align:right;"><h3 style="margin:0;color:#0F172A;">KWITANSI PEMBAYARAN</h3><span style="color:{theme['secondary']};font-family:monospace;">NO: {no_kwitansi}</span></div>
</div>
<div style="margin:15px 0;font-size:14px;">
<p style="margin:4px 0;"><strong>Telah Terima Dari:</strong> {terima_dari}</p>
<p style="margin:4px 0;color:{theme['primary']};"><strong>Uang Sejumlah:</strong> <i>"{terbilang}"</i></p>
</div>
<table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:10px;">
<thead><tr style="background-color:{theme['primary']};color:white;text-align:left;"><th style="padding:6px;">No</th><th style="padding:6px;">Nama Barang / Deskripsi</th><th style="padding:6px;text-align:right;">Qty</th><th style="padding:6px;text-align:right;">Harga Satuan</th><th style="padding:6px;text-align:right;">Subtotal</th></tr></thead>
<tbody>
{items_html}
<tr style="background-color:{theme['bg_light']};font-weight:bold;color:{theme['primary']};"><td colspan="4" style="padding:8px;text-align:right;">TOTAL BAYAR</td><td style="padding:8px;text-align:right;">{tot_fmt}</td></tr>
</tbody>
</table>
<div style="margin-top:30px;text-align:right;font-size:12px;color:#64748B;">
<p style="margin:0;">{kota}, {tanggal.strftime('%d %B %Y')}</p>
<p style="margin:0;">Penerima / Bendahara,</p>
<br><br>
<p style="margin:0;font-weight:bold;color:#0F172A;"><u>( {penerima} )</u></p>
</div>
</div>"""

st.components.v1.html(preview_html, height=450, scrolling=True)
