import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor
import qrcode
from PyPDF2 import PdfMerger
import zipfile

def generate_pdfs(entries, image_paths, logo_path, output_dir, template, merge):
    # Themes for seasonal backgrounds
    themes = {
        'summer': '#FFF8E1',
        'fall': '#FFECB3',
        'christmas': '#E1F5FE',
        'default': '#FFFFFF'
    }
    background = themes.get(template, '#FFFFFF')

    # Color map for swatch handling
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
        c = canvas.Canvas(file_path, pagesize=(792, 396))  # Half-Letter landscape size

        # Background color
        c.setFillColor(HexColor(background))
        c.rect(0, 0, 792, 396, fill=1, stroke=0)

        # Title
        c.setFillColor(HexColor('#000000'))
        c.setFont('Helvetica-Bold', 26)
        c.drawString(40, 360, f"{entry['Make']} {entry['Model']}")

        # Features
        c.setFont('Helvetica', 16)
        c.drawString(40, 320, "Features:")
        c.setFont('Helvetica', 14)
        y = 300
        for feat in ['Feature 1', 'Feature 2', 'Feature 3']:
            feature = entry.get(feat, '')
            if feature:
                c.drawString(60, y, f"• {feature}")
                y -= 20

        # Price Banner
        c.setFillColor(HexColor('#FFC107'))
        c.rect(40, 230, 300, 50, fill=1, stroke=0)
        c.setFillColor(HexColor('#000000'))
        c.setFont('Helvetica-Bold', 24)
        c.drawCentredString(190, 245, f"${entry['Price']}")

        # Colour Swatch
        c.setFillColor(HexColor('#000000'))
        c.setFont('Helvetica', 16)
        c.drawString(40, 180, "Colour:")

        color_name = entry.get('Color', 'red').lower()
        color_hex = COLOR_MAP.get(color_name, '#FF0000')  # Default to red if unknown

        c.setFillColor(HexColor(color_hex))
        c.rect(140, 170, 80, 30, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(180, 180, color_name.upper())

        # Product Image
        img_path = image_paths.get(entry['Image Filename'])
        if img_path:
            c.drawImage(img_path, 420, 130, width=320, height=220, preserveAspectRatio=True)

        # Logo
        if logo_path:
            c.drawImage(logo_path, 650, 300, width=100, preserveAspectRatio=True)

        # QR Code
        if entry.get('URL', '').startswith('http'):
            qr = qrcode.make(entry['URL'])
            qr_path = os.path.join(output_dir, 'temp_qr.png')
            qr.save(qr_path)
            c.drawImage(qr_path, 420, 40, width=50, height=50)
            c.setFont('Helvetica', 10)
            c.setFillColor(HexColor('#000000'))
            c.drawString(480, 60, "SEE MORE")
            os.remove(qr_path)

        c.showPage()
        c.save()
        pdf_paths.append(file_path)

    # Merge into one PDF or Zip
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
