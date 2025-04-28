import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor
import qrcode
from PyPDF2 import PdfMerger
import zipfile

def generate_pdfs(entries, image_paths, logo_path, output_dir, template, merge):
    # Themes for background colors
    themes = {
        'summer': '#FFF8E1',
        'fall': '#FFECB3',
        'christmas': '#E1F5FE',
        'default': '#FFFFFF'
    }
    background = themes.get(template, '#FFFFFF')

    # Color mapping for color swatches
    COLOR_MAP = {
        'red': '#FF0000',
        'black': '#000000',
        'blue': '#0000FF',
        'silver': '#C0C0C0',
        'white': '#FFFFFF',
        'gray': '#808080',
        'yellow': '#FFFF00',
        'green': '#00FF00',
        'orange': '#FFA500',
    }

    pdf_paths = []

    for entry in entries:
        file_path = os.path.join(output_dir, f"{entry['Make']}_{entry['Model']}.pdf".replace(' ', '_'))
        c = canvas.Canvas(file_path, pagesize=(792, 396))  # Half-Letter landscape

        # Background
        c.setFillColor(HexColor(background))
        c.rect(0, 0, 792, 396, fill=1, stroke=0)

        # Row 1: Product Name centered
        c.setFillColor(HexColor('#000000'))
        c.setFont('Helvetica-Bold', 28)
        c.drawCentredString(396, 360, f"{entry['Make']} {entry['Model']}")

        # Row 2: Product Image centered
        img_path = image_paths.get(entry['Image Filename'])
        if img_path:
            c.drawImage(img_path, 196, 190, width=400, height=150, preserveAspectRatio=True, anchor='c')

        # Row 3: Two columns
        # Left Column - Features
        c.setFont('Helvetica-Bold', 16)
        c.drawString(40, 170, "Features:")
        c.setFont('Helvetica', 14)
        feature_y = 150
        for feat in ['Feature 1', 'Feature 2', 'Feature 3']:
            feature = entry.get(feat, '')
            if feature:
                c.drawString(60, feature_y, f"• {feature}")
                feature_y -= 20

        # Left Column - Price
        c.setFillColor(HexColor('#FFC107'))
        c.rect(40, 60, 200, 50, fill=1, stroke=0)
        c.setFillColor(HexColor('#000000'))
        c.setFont('Helvetica-Bold', 22)
        c.drawCentredString(140, 75, f"${entry['Price']}")

        # Right Column - Colors
        c.setFont('Helvetica-Bold', 16)
        c.drawString(520, 170, "Colour:")
        color_name = entry.get('Color', 'red').lower()
        color_hex = COLOR_MAP.get(color_name, '#FF0000')
        c.setFillColor(HexColor(color_hex))
        c.rect(620, 160, 80, 30, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(660, 170, color_name.upper())

        # Right Column - QR Code at bottom
        if entry.get('URL', '').startswith('http'):
            qr = qrcode.make(entry['URL'])
            qr_path = os.path.join(output_dir, 'temp_qr.png')
            qr.save(qr_path)
            c.drawImage(qr_path, 520, 40, width=60, height=60)
            c.setFont('Helvetica', 10)
            c.setFillColor(HexColor('#000000'))
            c.drawString(590, 60, "SEE MORE")
            os.remove(qr_path)

        # Logo (optional, at bottom right corner)
        if logo_path:
            c.drawImage(logo_path, 680, 40, width=80, height=40, preserveAspectRatio=True, mask='auto')

        c.showPage()
        c.save()
        pdf_paths.append(file_path)

    if merge:
        merged_path = os.path.join(output_dir, 'All_Adverts.pdf')
        merger = PdfMerger()
        for pdf in pdf_paths:
            merger.append(pdf)
        merger.write(merged_path)
        merger.close()
        return [merged_path]
    else:
        zip_path = os.path.join(output_dir, 'adverts.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in pdf_paths:
                zipf.write(pdf, os.path.basename(pdf))
        return [zip_path]
