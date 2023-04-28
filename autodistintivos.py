"""
Genera distintivos automáticamente.
"""

__version__ = "0.1.dev0"


import logging
import urllib.parse
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import click
import qrcode
import structlog
from pypdf import PdfReader, PdfWriter
from qrcode.image.pil import PilImage
from reportlab.pdfgen import canvas

logger = structlog.get_logger()


@dataclass
class TemplateSpec:
    filename: str

    logo_x_ref: int
    logo_y_ref: int
    logo_width: int
    logo_height: int

    qr_x_ref: int | None = None
    qr_y_ref: int | None = None
    qr_width: int | None = None
    qr_height: int | None = None


def qr_from_text(text: str, box_size_px=100) -> PilImage:
    qr = qrcode.QRCode(
        version=1,
        box_size=box_size_px,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="transparent")
    return img


def logo_filename_from_url(logo_url: str) -> str:
    logo_filename_encoded = logo_url.rsplit("/", maxsplit=1)[-1]
    return urllib.parse.unquote(logo_filename_encoded)


def generate(
    template_spec: TemplateSpec,
    logo_path: Path,
    destination: Path,
    qr_path: Path | None = None,
):
    # Adapted from https://stackoverflow.com/a/10766606/554319
    # Using ReportLab to insert image into PDF
    logo_bytes = BytesIO()
    logo_canvas = canvas.Canvas(logo_bytes)

    # Draw image on Canvas and save PDF in buffer
    logo_canvas.drawImage(
        logo_path,
        x=template_spec.logo_x_ref,
        y=template_spec.logo_y_ref,
        width=template_spec.logo_width,
        height=template_spec.logo_height,
        mask="auto",
        preserveAspectRatio=True,
        anchor="c",
    )
    logo_canvas.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfReader(template_spec.filename).pages[0]
    overlay = PdfReader(logo_bytes).pages[0]

    page.merge_page(overlay)

    if qr_path:
        qr_bytes = BytesIO()
        qr_canvas = canvas.Canvas(qr_bytes)

        qr_canvas.drawImage(
            qr_path,
            x=template_spec.qr_x_ref,
            y=template_spec.qr_y_ref,
            width=template_spec.qr_width,
            height=template_spec.qr_height,
            mask="auto",
            preserveAspectRatio=True,
            anchor="c",
        )
        qr_canvas.save()

        qr = PdfReader(BytesIO(qr_bytes.getvalue())).pages[0]
        page.merge_page(qr)

    # Save the result
    output = PdfWriter()
    output.add_page(page)
    with open(destination, "wb") as fh:
        output.write(fh)


def generate_from_data(
    name, logo_url, template_spec: TemplateSpec, logos_dir, destination_dir
):
    logo_filename = Path(logos_dir) / f"{logo_filename_from_url(logo_url)}"
    destination = Path(destination_dir) / f"{name}.pdf"

    if not logo_filename.is_file():
        raise FileNotFoundError("No se encontró el logo")
    elif not destination.parent.is_dir():
        raise FileNotFoundError("No se encontró el directorio de destino")

    generate(template_spec, logo_filename, destination)


def generate_from_logos(
    logos_directory: Path,
    template_spec: TemplateSpec,
    destination_dir: Path,
    qrs_dir: Path | None = None,
):
    for logo_path in logos_directory.rglob("*.png"):
        destination = destination_dir / f"{logo_path.stem}.pdf"

        # FIXME: Refactor
        if qrs_dir:
            qr_path = qrs_dir / f"{logo_path.stem}.png"
            if not qr_path.is_file():
                # FIXME: Load URL dynamically
                qr_image = qr_from_text("https://madrid.mercadosocial.net")
                qr_image.save(qr_path)
        else:
            qr_path = None

        generate(
            template_spec,
            logo_path,
            destination,
            qr_path,
        )

        logger.info("Generado distintivo", logo_filename=logo_path.stem)


@click.command()
@click.option("--template", required=True)
@click.option("--template-logo-xy", required=True, type=(int, int))
@click.option("--template-logo-wh", required=True, type=(int, int))
@click.option("--template-qr-xy", type=(int, int))
@click.option("--template-qr-wh", type=(int, int))
@click.option("--logos-dir", type=click.Path(), default="logos")
@click.option("--qrs-dir", type=click.Path())
@click.option("--destination-dir", type=click.Path(), default="distintivos")
def cli(
    template,
    template_logo_xy,
    template_logo_wh,
    template_qr_xy,
    template_qr_wh,
    logos_dir,
    qrs_dir,
    destination_dir,
):
    if template_logo_xy is not None and template_qr_wh is not None:
        template_spec = TemplateSpec(
            template,
            *template_logo_xy,
            *template_logo_wh,
            *template_qr_xy,
            *template_qr_wh,
        )
    else:
        template_spec = TemplateSpec(template, *template_logo_xy, *template_logo_wh)

    generate_from_logos(
        Path(logos_dir),
        template_spec,
        Path(destination_dir),
        Path(qrs_dir) if qrs_dir else None,
    )


if __name__ == "__main__":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO)
    )

    cli()
