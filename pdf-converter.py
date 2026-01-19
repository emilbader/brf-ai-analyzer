# Run with: pymupdf-venv/bin/python ./pdf-converter.py <path-to-pdf>
import pymupdf
import sys
import os
from pathlib import Path


def convert_pdf_to_markdown(pdf_path):
    """
    Convert a PDF file to markdown format.
    
    Args:
        pdf_path: Path to the PDF file to convert
        
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
    
    # Open PDF and convert
    doc = pymupdf.open(pdf_path)
    page_count = len(doc)
    
    with open(output_path, "w", encoding="utf-8") as out:
        # Process each page
        for page_num in range(page_count):
            page = doc[page_num]
            # Extract text - get_text() with no args or "text" returns plain text string
            text = page.get_text()
            
            # Ensure text is a string before writing
            if isinstance(text, str) and text.strip():
                out.write(text)
                out.write("\n\n---\n\n")  # Page separator
    
    doc.close()
    
    print(f"Processed {page_count} pages successfully")
    print(f"Output written to: {output_path}")
    
    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: pymupdf-venv/bin/python ./pdf-converter.py <path-to-pdf>")
        print("Example: pymupdf-venv/bin/python ./pdf-converter.py documents/original/arsredovisning-brf-killingen-39.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        convert_pdf_to_markdown(pdf_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

