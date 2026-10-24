
from pathlib import Path
from pypdf import PdfReader

PROJECT_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = PROJECT_DIR / "backend" / "documents"


def read_pdf():
    print("Searching for PDF files...")

    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in: {DOCUMENTS_DIR}")
        return

    print(f"\nFound {len(pdf_files)} PDF file(s).")

    for pdf_path in pdf_files:
        print("\n" + "=" * 70)
        print(f"FILENAME: {pdf_path.name}")
        print("=" * 70)

        try:
            reader = PdfReader(str(pdf_path))

            print(f"Total pages: {len(reader.pages)}")

            # Inspect the first three pages of each PDF.
            for page_number, page in enumerate(
                reader.pages[:3], start=1
            ):
                text = page.extract_text() or ""

                print(f"\n--- PAGE {page_number} ---")

                if text.strip():
                    print(text[:3000])
                else:
                    print(
                        "No extractable text on this page. "
                        "It may contain scanned or image-based content."
                    )

        except Exception as error:
            print(f"Could not read {pdf_path.name}: {error}")


if __name__ == "__main__":
    read_pdf()
