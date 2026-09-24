import base64
import io

import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer


def generate_qr(value: str):
    fill_color = (25, 55, 90)
    background_color = (255, 255, 255)
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=12,
        border=2,
    )

    qr.add_data(value)
    qr.make(fit=True)

    qr_image = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(
            front_color=fill_color,
            back_color=background_color,
        ),
    ).convert("RGB")

    title_height = 20
    image = Image.new(
        "RGB",
        (qr_image.width, qr_image.height + title_height),
        background_color,
    )
    image.paste(qr_image, (0, 0))
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default(size=18)
    title = value.lower()

    bbox = draw.textbbox((0, 0), title, font=font, stroke_width=0.1, spacing=6)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (image.width - text_width) // 2
    text_y = (qr_image.height + (title_height - text_height) // 2) - 20

    draw.text(
        (text_x, text_y),
        title,
        fill=fill_color,
        font=font,
        stroke_width=0.1,
        spacing=6,
    )

    return image


def qr_to_base64(value: str) -> str:
    image = generate_qr(value)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    text = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{text}"
