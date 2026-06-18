import os
import fitz
import pikepdf
import subprocess
import tempfile


def compress_pdf(input_path, output_path, mode="balanced"):

    gs_path = r"C:\Program Files\gs\gs10.07.1\bin\gswin64c.exe"
    qpdf_path = r"C:\Program Files\qpdf 12.3.2\bin\qpdf.exe"

    temp_clean = tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    ).name

    temp_gs = tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    ).name

    temp_pike = tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    ).name

    try:

        # ==========================
        # STEP 1 - CLEAN PDF
        # ==========================

        doc = fitz.open(input_path)

        try:
            doc.set_metadata({})
        except:
            pass

        try:
            doc.del_xml_metadata()
        except:
            pass

        doc.save(
            temp_clean,
            garbage=4,
            clean=True,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
            use_objstms=1
        )

        doc.close()

        # ==========================
        # COMPRESSION MODE
        # ==========================

        if mode == "balanced":

            pdf_settings = "/ebook"
            image_resolution = "150"
            jpeg_quality = "70"

        else:

            pdf_settings = "/screen"
            image_resolution = "96"
            jpeg_quality = "45"

        # ==========================
        # STEP 2 - GHOSTSCRIPT
        # ==========================

        subprocess.run(
            [
                gs_path,

                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",

                f"-dPDFSETTINGS={pdf_settings}",

                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",

                "-dDetectDuplicateImages=true",
                "-dCompressFonts=true",
                "-dSubsetFonts=true",

                "-dDownsampleColorImages=true",
                "-dColorImageDownsampleType=/Bicubic",
                f"-dColorImageResolution={image_resolution}",

                "-dDownsampleGrayImages=true",
                "-dGrayImageDownsampleType=/Bicubic",
                f"-dGrayImageResolution={image_resolution}",

                "-dAutoFilterColorImages=false",
                "-dColorImageFilter=/DCTEncode",

                "-dAutoFilterGrayImages=false",
                "-dGrayImageFilter=/DCTEncode",

                f"-dJPEGQ={jpeg_quality}",

                f"-sOutputFile={temp_gs}",

                temp_clean
            ],
            check=True
        )

        # ==========================
        # STEP 3 - PIKEPDF
        # ==========================

        with pikepdf.open(temp_gs) as pdf:

            try:
                pdf.remove_unreferenced_resources()
            except:
                pass

            pdf.save(
                temp_pike,
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate
            )

        # ==========================
        # STEP 4 - QPDF
        # ==========================

        subprocess.run(
            [
                qpdf_path,
                "--linearize",
                temp_pike,
                output_path
            ],
            check=True
        )

        # ==========================
        # RESULTS
        # ==========================

        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)

        reduction = round(
            (
                (original_size - compressed_size)
                / original_size
            ) * 100,
            2
        )

        return {
            "original_size": round(
                original_size / 1024 / 1024,
                2
            ),
            "compressed_size": round(
                compressed_size / 1024 / 1024,
                2
            ),
            "reduction": reduction
        }

    finally:

        for temp_file in [
            temp_clean,
            temp_gs,
            temp_pike
        ]:

            if os.path.exists(temp_file):
                os.remove(temp_file)