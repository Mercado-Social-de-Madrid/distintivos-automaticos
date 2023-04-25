"""
Genera distintivos automáticamente.
"""

__version__ = "0.1.dev0"


import csv
import logging
from io import BytesIO
from pathlib import Path

import click
import structlog
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

logger = structlog.get_logger()


def generate(template, logo, destination):
    # Adapted from https://stackoverflow.com/a/10766606/554319
    # Using ReportLab to insert image into PDF
    logo_bytes = BytesIO()
    logo_canvas = canvas.Canvas(logo_bytes)

    # Draw image on Canvas and save PDF in buffer
    logo_canvas.drawImage(
        logo,
        x=250,
        y=500,
        width=80,
        height=80,
        mask="auto",
        preserveAspectRatio=True,
        anchor="c",
    )
    logo_canvas.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfReader(open(template, "rb")).pages[0]
    overlay = PdfReader(BytesIO(logo_bytes.getvalue())).pages[0]
    page.merge_page(overlay)

    # Save the result
    output = PdfWriter()
    output.add_page(page)
    with open(destination, "wb") as fh:
        output.write(fh)


def generate_from_data(name, logo_url, template, logos_dir, destination_dir):
    logo_filename = Path(logos_dir) / f"{logo_url.rsplit('/', maxsplit=1)[-1]}"
    destination = Path(destination_dir) / f"{name}.pdf"

    if not logo_filename.is_file():
        raise FileNotFoundError("Logo not found")
    elif not destination.parent.is_dir():
        raise FileNotFoundError("Destination directory not found")

    generate(template, logo_filename, destination)


@click.command()
@click.option("--data-file", required=True)
@click.option("--template", required=True)
@click.option("--logos-dir", default="logos")
@click.option("--destination-dir", default="distintivos")
def cli(data_file, template, logos_dir, destination_dir):
    with open(data_file) as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader)  # CSV header
        for name, logo_url, *rest in reader:
            if not name or not logo_url:
                logger.warning(
                    "Datos inválidos, no se generó el distintivo",
                    name=name,
                    logo_url=logo_url,
                )
            else:
                try:
                    generate_from_data(
                        name, logo_url, template, logos_dir, destination_dir
                    )
                except Exception as e:
                    logger.error("No se pudo generar el distintivo", error=e, name=name)
                else:
                    logger.info("Distintivo generado con éxito", name=name)


if __name__ == "__main__":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO)
    )

    cli()
