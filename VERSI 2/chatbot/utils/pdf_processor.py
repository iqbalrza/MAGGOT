"""
PDF Processor with OCR using Tesseract
Extract text and images/tables from PDF using OCR
"""

import os
import io
from typing import List, Dict, Tuple
from pathlib import Path
import base64

from PIL import Image
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np


class PDFProcessor:
    """Process PDF files: extract text using OCR (Tesseract)"""
    
    def __init__(self, tesseract_cmd: str = None, lang: str = "eng"):
        """
        Initialize PDF Processor with OCR
        
        Args:
            tesseract_cmd: Path to tesseract executable (optional)
            lang: OCR language (default: 'eng', use 'eng+ind' for English+Indonesian)
        """
        # Set tesseract command if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif os.name == 'nt':  # Windows
            # Common Windows installation paths
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        self.lang = lang
        print(f"✅ PDF Processor initialized with Tesseract OCR (lang: {lang})")
    
    def preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get better text detection
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Convert back to PIL
        return Image.fromarray(denoised)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text from PDF (native text extraction first)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num} ---\n{page_text}\n"
            
            return text.strip()
        
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return ""
    
    def extract_images_from_pdf(self, pdf_path: str, output_dir: str = None) -> List[str]:
        """
        Extract images from PDF by converting pages to images
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted images
            
        Returns:
            List of image file paths
        """
        try:
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(pdf_path), "extracted_images")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Convert PDF pages to images
            print(f"   Converting PDF to images (this may take a while)...")
            images = convert_from_path(pdf_path, dpi=300)  # Higher DPI for better OCR
            
            image_paths = []
            pdf_name = Path(pdf_path).stem
            
            for i, image in enumerate(images):
                image_path = os.path.join(output_dir, f"{pdf_name}_page_{i+1}.png")
                image.save(image_path, "PNG")
                image_paths.append(image_path)
            
            print(f"✅ Extracted {len(image_paths)} page images from PDF")
            return image_paths
        
        except Exception as e:
            print(f"❌ Error extracting images: {e}")
            return []
    
    def ocr_image(self, image_path: str = None, image: Image.Image = None) -> str:
        """
        Perform OCR on an image using Tesseract
        
        Args:
            image_path: Path to image file (optional if image is provided)
            image: PIL Image object (optional if image_path is provided)
            
        Returns:
            Extracted text from image
        """
        try:
            if image is None:
                if image_path is None:
                    raise ValueError("Either image_path or image must be provided")
                image = Image.open(image_path).convert("RGB")
            
            # Preprocess image for better OCR
            preprocessed = self.preprocess_image_for_ocr(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(preprocessed, lang=self.lang)
            
            return text.strip()
        
        except Exception as e:
            print(f"❌ Error performing OCR: {e}")
            return ""
    
    def process_pdf_full(self, pdf_path: str, skip_ocr: bool = False) -> Dict[str, any]:
        """
        Complete PDF processing: extract text + OCR images
        
        Args:
            pdf_path: Path to PDF file
            skip_ocr: Skip OCR processing (faster, only native text extraction)
            
        Returns:
            Dictionary with:
                - full_text: All text from PDF (native extraction)
                - ocr_text: Text extracted via OCR from images
                - combined_text: Text + OCR text combined
                - num_images: Number of page images processed
        """
        print(f"📄 Processing PDF: {pdf_path}")
        
        # Extract text using native PDF extraction
        print("📝 Extracting text (native)...")
        native_text = self.extract_text_from_pdf(pdf_path)
        
        ocr_text = ""
        num_images = 0
        
        if not skip_ocr:
            # Convert PDF to images and perform OCR
            print("🖼️ Converting PDF to images for OCR...")
            image_paths = self.extract_images_from_pdf(pdf_path)
            num_images = len(image_paths)
            
            # Perform OCR on each page image
            print("🔍 Performing OCR on page images...")
            ocr_results = []
            for i, img_path in enumerate(image_paths, 1):
                print(f"  OCR processing page {i}/{len(image_paths)}...")
                ocr_text_page = self.ocr_image(image_path=img_path)
                
                if ocr_text_page:
                    ocr_results.append(f"\n--- OCR Page {i} ---\n{ocr_text_page}")
            
            ocr_text = "\n".join(ocr_results)
        
        # Combine native text and OCR text
        combined_text = native_text
        if ocr_text:
            combined_text += f"\n\n--- OCR EXTRACTED TEXT ---\n{ocr_text}"
        
        result = {
            "pdf_path": pdf_path,
            "full_text": native_text,
            "ocr_text": ocr_text,
            "combined_text": combined_text,
            "num_images": num_images
        }
        
        print(f"✅ PDF processing complete!")
        print(f"   - Native text length: {len(native_text)} chars")
        print(f"   - OCR text length: {len(ocr_text)} chars")
        print(f"   - Combined length: {len(combined_text)} chars")
        print(f"   - Pages processed: {num_images}")
        
        return result
