"""
Genera distintivos automáticamente.
"""

__version__ = "0.1.dev0"


import csv
import logging
import urllib.parse
from copy import copy
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

    generate_qr: bool = False
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
    destination_path: Path,
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
    with open(destination_path, "wb") as fh:
        output.write(fh)


def generate_from_data(
    name: str,
    logo_url: str,
    template_spec: TemplateSpec,
    info_url: str | None = None,
    logos_dir: Path = Path("logos"),
    destination_dir: Path = Path("distintivos"),
    qrs_dir: Path = Path("qrs"),
    overwrite: bool = False,
):
    logo_path = logos_dir / f"{logo_filename_from_url(logo_url)}"
    destination_path = destination_dir / f"{name}.pdf"

    if destination_path.is_file() and not overwrite:
        logger.warning(
            "Distintivo existente, no se sobreescribirá",
            destination_path=destination_path,
        )
        return

    if not logo_path.is_file():
        raise FileNotFoundError("No se encontró el logo")
    elif not destination_path.parent.is_dir():
        raise FileNotFoundError("No se encontró el directorio de destino")

    if template_spec.generate_qr:
        if not qrs_dir.is_dir():
            raise FileNotFoundError("No se encontró el directorio de códigos QR")

        qr_path = qrs_dir / f"{logo_path.stem}.png"
        if not qr_path.is_file():
            qr_image = qr_from_text(info_url)
            qr_image.save(qr_path)
    else:
        qr_path = None

    logger.debug(
        "Generando distintivo",
        template_spec=template_spec,
        logo_path=logo_path,
        destination_path=destination_path,
        qr_path=qr_path,
    )
    generate(template_spec, logo_path, destination_path, qr_path)


@click.command()
@click.option("--data-file", type=click.Path(), required=True)
@click.option("--template", required=True)
@click.option("--template-logo-xy", required=True, type=(int, int))
@click.option("--template-logo-wh", required=True, type=(int, int))
@click.option("--template-qr-xy", type=(int, int))
@click.option("--template-qr-wh", type=(int, int))
@click.option("--logos-dir", type=click.Path(), default="logos")
@click.option("--qrs-dir", type=click.Path(), default="qrs")
@click.option("--destination-dir", type=click.Path(), default="distintivos")
@click.option("--overwrite", is_flag=True)
@click.option("--verbose", "-v", is_flag=True)
def cli(
    data_file,
    template,
    template_logo_xy,
    template_logo_wh,
    template_qr_xy,
    template_qr_wh,
    logos_dir,
    qrs_dir,
    destination_dir,
    overwrite,
    verbose,
):
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if verbose else logging.WARNING
        )
    )

    if template_logo_xy is not None and template_qr_wh is not None:
        base_template_spec = TemplateSpec(
            template,
            *template_logo_xy,
            *template_logo_wh,
            True,
            *template_qr_xy,
            *template_qr_wh,
        )
    else:
        base_template_spec = TemplateSpec(
            template, *template_logo_xy, *template_logo_wh
        )

    with open(data_file) as csv_file:
        reader = csv.reader(csv_file, delimiter=";")
        next(reader)  # CSV header
        for name, logo_url, info_url, *rest in reader:
            if not name or not logo_url:
                logger.warning(
                    "Datos inválidos, no se generó el distintivo",
                    name=name,
                    logo_url=logo_url,
                )
            else:
                if all(rest):
                    # Override template spec
                    template_spec = copy(base_template_spec)
                    (
                        template_spec.logo_x_ref,
                        template_spec.logo_y_ref,
                        template_spec.logo_width,
                        template_spec.logo_height,
                    ) = [int(v) for v in rest]
                else:
                    template_spec = base_template_spec

                try:
                    generate_from_data(
                        name,
                        logo_url,
                        template_spec,
                        info_url,
                        Path(logos_dir),
                        Path(destination_dir),
                        Path(qrs_dir),
                        overwrite,
                    )
                except Exception as e:
                    logger.error("No se pudo generar el distintivo", error=e, name=name)
                else:
                    logger.info("Distintivo generado con éxito", name=name)


if __name__ == "__main__":
    cli()
