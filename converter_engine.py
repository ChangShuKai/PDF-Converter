import os
import img2pdf
import fitz  # PyMuPDF
from PIL import Image
import io

class PDFConverterEngine:
    @staticmethod
    def images_to_pdf(image_paths, output_path):
        """
        Converts a list of images to a single PDF losslessly.
        img2pdf embeds the image data directly without re-compression.
        """
        try:
            with open(output_path, "wb") as f:
                # img2pdf.convert takes a list of file paths or binary streams
                f.write(img2pdf.convert(image_paths))
            return True, "Successfully converted images to PDF."
        except Exception as e:
            return False, f"Error in Image-to-PDF: {str(e)}"

    @staticmethod
    def pdf_to_images(pdf_path, output_folder, dpi=300):
        """
        Extracts each page of a PDF as a high-quality image.
        Uses PyMuPDF (fitz) for high performance and quality.
        """
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            doc = fitz.open(pdf_path)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            saved_files = []
            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                
                # Use a matrix for high DPI scaling
                zoom = dpi / 72  # 72 is the default DPI
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                
                output_filename = f"{base_name}_page_{page_index + 1}.png"
                output_path = os.path.join(output_folder, output_filename)
                
                pix.save(output_path)
                saved_files.append(output_path)
                
            doc.close()
            return True, f"Successfully extracted {len(saved_files)} pages to {output_folder}"
        except Exception as e:
            return False, f"Error in PDF-to-Image: {str(e)}"

# Example usage (commented out):
# engine = PDFConverterEngine()
# engine.images_to_pdf(["image1.jpg", "image2.png"], "output.pdf")
# engine.pdf_to_images("input.pdf", "output_images_folder")
