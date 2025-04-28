import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape
from reportlab.lib.colors import HexColor
from PIL import Image
import qrcode
from PyPDF2 import PdfMerger
import zipfile

def remove_background(image_path):
    """Automatically removes white-ish background from product image."""
    image = Image.open(image_path).convert("RGBA")
    datas = image.getdata()

    newData = []
    for item in datas:
        # If pixel is almost white, make transparent
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    image.putdata(newData)

    # Save transparent image temporarily
    temp_path = image_path.replace(".", "_transparent.")
    image.save(temp_path, "PNG")
    return temp_path

def generate_pdfs(entries, image_paths, logo_path, output_dir, template, merge):
    themes = {
        'summer': '#FFF8E1',
        'fall': '#FFECB3',
        'christmas': '#E1F5FE',
        'default': '#FFFFFF'
    }
    background = themes.get(template, '#FFFFFF')

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

        # Page Background
        c.setFillColor(HexColor(background))
        c.rect(0, 0, 792, 396, fill=1, stroke=0)

        # Title Row
        c.setFillColor(HexColor('#D9EAF7'))  # Light blue
        c.rect(0, 330, 792, 66, fill=1, stroke=0)

        c.setFillColor(HexColor('#000000'))
        c.setFont('Helvetica-Bold', 28)
        c.drawCentredString(396, 360, f"{entry['Make']} {entry['Model']}")

        # Product Image Background
        c.setFillColor(HexColor('#F0F0F0'))  # Light gray
        c.rect(0, 170, 792, 160, fill=1, stroke=0)

        # Product Image (centered)
        img_path = image_paths.get(entry['Image Filename'])
        if img_path:
            transparent_img = remove_background(img_path)
            c.drawImage(transparent_img, 196, 190, width=400, height=140, preserveAspectRatio=True, mask='auto')
            os.remove(transparent_img)

        # Features (Left Column)
        c.setFont('Helvetica-Bold', 16)
        c.setFillColor(HexColor('#000000'))
        c.drawString(40, 150, "Features:")

        c.setFont('Helvetica', 14)
        feature_y = 130
        for feat in ['Feature 1', 'Feature 2', 'Feature 3']:
            feature = entry.get(feat, '')
            if feature:
                c.drawString(60, feature_y, f"• {feature}")
                feature_y -= 20

        # Price Section (Separated Better)
        c.setFont('Helvetica-Bold', 16)
        c.drawString(40, 75, "Price:")

        c.setFillColor(HexColor('#FFC107'))
        c.rect(40, 20, 260, 45, fill=1, stroke=0)

        c.setFillColor(HexColor('#000000'))
        c.setFont('Helvetica-Bold', 24)
        c.drawCentredString(170, 38, f"${entry['Price']}")

        # Right Column: Color Swatch
        c.setFont('Helvetica-Bold', 16)
        c.setFillColor(HexColor('#000000'))
        c.drawString(520, 150, "Colour:")

        color_name = entry.get('Color', 'red').lower()
        color_hex = COLOR_MAP.get(color_name, '#FF0000')

        c.setFillColor(HexColor(color_hex))
        c.rect(620, 140, 80, 30, fill=1, stroke=0)

        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(660, 150, color_name.upper())

        # QR Code (Bottom-Right)
        if entry.get('URL', '').startswith('http'):
            qr = qrcode.make(entry['URL'])
            qr_path = os.path.join(output_dir, 'temp_qr.png')
            qr.save(qr_path)
            c.drawImage(qr_path, 700, 20, width=60, height=60)
            c.setFont('Helvetica', 10)
            c.setFillColor(HexColor('#000000'))
            c.drawString(760, 40, "SEE MORE")
            os.remove(qr_path)

        # Logo (Optional - near QR)
        if logo_path:
            c.drawImage(logo_path, 620, 20, width=60, height=40, preserveAspectRatio=True, mask='auto')

        c.showPage()
        c.save()
        pdf_paths.append(file_path)

    # Merging PDFs
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
