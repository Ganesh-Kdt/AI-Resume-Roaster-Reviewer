import base64, io
from pdf2image import convert_from_bytes
from PIL import Image

def pdf_pages_to_base64_images(pdf_bytes, dpi=200, max_dim=1600):
    """
    Convert each PDF page to a base-64 PNG string suitable for GPT-Vision.
    Returns a list of content blocks for Chat Completions vision:
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
    """
    pagesImage = convert_from_bytes(pdf_bytes, dpi=dpi)       
    msgs  = []
    for img in pagesImage:
        #resize to stay under 4096×4096 vision limits
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        msgs.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"}
            }
        )
    return msgs