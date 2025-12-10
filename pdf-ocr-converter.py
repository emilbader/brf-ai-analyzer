#!/usr/bin/env python3
"""
PDF to Markdown converter with OCR support for scanned documents.
Run with: pymupdf-venv/bin/python ./pdf-ocr-converter.py <path-to-pdf> [language]

This script uses Tesseract OCR to extract text from image-based PDFs.
Requires Tesseract to be installed: brew install tesseract tesseract-lang
"""

import pymupdf
import sys
import os
from pathlib import Path


def convert_pdf_to_markdown_with_ocr(pdf_path, language="swe", dpi=600):
    """
    Convert a PDF file (including scanned/image PDFs) to markdown format using OCR.
    
    Args:
        pdf_path: Path to the PDF file to convert
        language: Tesseract language code (default: "swe" for Swedish)
        dpi: DPI resolution for OCR (default: 600)
        
    Returns:
        Path to the generated markdown file
    """
    # Validate input file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Get the filename without extension
    pdf_filename = Path(pdf_path).stem
    
    # Create output directory if it doesn't exist
    output_dir = Path("documents/converted")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create output file path
    output_path = output_dir / f"{pdf_filename}.md"
    
    print(f"Opening PDF: {pdf_path}")
    doc = pymupdf.open(pdf_path)
    page_count = len(doc)
    print(f"Processing {page_count} pages with OCR (language: {language}, dpi: {dpi})...")
    
    with open(output_path, "w", encoding="utf-8") as out:
        # Process each page
        for page_num in range(page_count):
            page = doc[page_num]
            
            # First try to get regular text
            text = page.get_text()
            
            # Ensure text is a string
            if not isinstance(text, str):
                text = ""
            
            # If page has no text or very little text, use OCR
            if not text or len(text.strip()) < 50:
                print(f"  Page {page_num + 1}/{page_count}: Using OCR (no text layer detected)")
                
                try:
                    # Get TextPage with OCR
                    # flags=0 gives cleaner output (no bounding boxes/coordinates)
                    # tessdata=None uses default tessdata path
                    textpage = page.get_textpage_ocr(
                        flags=0,           # 0 for clean text, 3 for detailed info
                        language=language,
                        dpi=dpi,
                        full=True,         # Process entire page
                        tessdata=None      # Use default tessdata location
                    )
                    text = textpage.extractText()
                    
                    # Clean up OCR artifacts
                    if text:
                        import re
                        
                        # Remove excessive whitespace and clean up common OCR errors
                        lines = text.split('\n')
                        cleaned_lines = []
                        
                        for line in lines:
                            stripped = line.strip()
                            
                            # Skip empty lines
                            if len(stripped) == 0:
                                continue
                            
                            # Skip lines that are mostly single characters separated by spaces
                            # (like "C C LE [ [0]")
                            single_char_pattern = re.match(r'^([A-ZÅÄÖ\[\]\(\)]{1,2}\s+){3,}', stripped)
                            if single_char_pattern:
                                continue
                            
                            # Count different character types
                            alnum_count = sum(c.isalnum() or c.isspace() for c in stripped)
                            total_chars = len(stripped)
                            
                            # Skip if less than 40% normal characters
                            if total_chars > 0 and (alnum_count / total_chars) < 0.4:
                                continue
                            
                            # Remove excessive repeated patterns (like "RR RR RR" or "KR KR KR")
                            cleaned = stripped
                            
                            # Remove repeated uppercase abbreviations (2-3 letters)
                            cleaned = re.sub(r'\b([A-ZÅÄÖ]{1,3})\s+\1(\s+\1){2,}\b', '', cleaned)
                            
                            # Remove lines that are just dots and spaces
                            if re.match(r'^[\.\s]+$', cleaned):
                                continue
                            
                            # Remove excessive punctuation patterns (like ".....ssssss")
                            cleaned = re.sub(r'\.{3,}', '...', cleaned)
                            cleaned = re.sub(r'-{3,}', '---', cleaned)
                            
                            # Remove repeated single characters (like "s s s s s")
                            cleaned = re.sub(r'\b(\w)\s+\1(\s+\1){3,}\b', '', cleaned)
                            
                            # Normalize whitespace
                            cleaned = re.sub(r'\s+', ' ', cleaned)
                            
                            # Skip if line became too short after cleaning
                            if len(cleaned.strip()) < 3:
                                continue
                            
                            # Skip lines that are just page numbers or odd fragments
                            if re.match(r'^[\d\s\-\/]+$', cleaned.strip()):
                                continue
                            
                            # Skip lines with excessive special characters still remaining
                            special_count = sum(not c.isalnum() and not c.isspace() for c in cleaned)
                            if special_count > len(cleaned) * 0.6:  # More than 60% special chars
                                continue
                            
                            cleaned_lines.append(cleaned.strip())
                        
                        text = '\n'.join(cleaned_lines)
                    
                    if not text or len(text.strip()) < 10:
                        print(f"    Warning: OCR returned minimal text for page {page_num + 1}")
                        text = f"[OCR returned minimal text for page {page_num + 1}]"
                        
                except Exception as e:
                    print(f"    Warning: OCR failed for page {page_num + 1}: {e}")
                    text = f"[OCR failed for page {page_num + 1}]"
            else:
                print(f"  Page {page_num + 1}/{page_count}: Using existing text layer")
            
            # Write text to output file
            if text and text.strip():
                out.write(text)
                out.write("\n\n---\n\n")  # Page separator
    
    doc.close()
    
    print(f"\n✓ Processed {page_count} pages successfully")
    print(f"✓ Output written to: {output_path}")
    
    # Show file size
    file_size = output_path.stat().st_size
    print(f"✓ Output file size: {file_size:,} bytes")
    
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pymupdf-venv/bin/python ./pdf-ocr-converter.py <path-to-pdf> [language] [dpi]")
        print("Example: pymupdf-venv/bin/python ./pdf-ocr-converter.py documents/original/arsredovisning.pdf swe 600")
        print("\nCommon language codes:")
        print("  swe - Swedish")
        print("  eng - English")
        print("  nor - Norwegian")
        print("  dan - Danish")
        print("\nDefault: language=swe, dpi=600")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "swe"
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    
    try:
        convert_pdf_to_markdown_with_ocr(pdf_path, language, dpi)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)