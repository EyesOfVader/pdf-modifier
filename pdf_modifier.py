from PyPDF2 import PdfFileReader, PdfFileWriter
from pdfminer.high_level import extract_text_to_fp


def read_pdf_info(file_path):
    with open(file_path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        return {
            'Author': info.author,
            'Title': info.title,
            'Page Count': pdf.getNumPages(),
            'Subject': info.subject,
            'File Path': file_path
        }

def rotate_page(file_path, page_number, direction, angle):
    writer = PdfFileWriter()
    reader = PdfFileReader(file_path)
    for x in range(reader.getNumPages()):
        page = reader.getPage(x)
        if x + 1 == page_number:
            if direction == 'clockwise':
                page.rotateClockwise(angle)
            else:
                page.rotateCounterClockwise(angle)
        writer.addPage(page)
    with open(file_path, 'wb') as f:
        writer.write(f)


def merge_pdfs(file_paths, output_path='output.pdf'):
    writer = PdfFileWriter()

    for file_path in file_paths:
        reader = PdfFileReader(file_path)
        for page in range(reader.getNumPages()):
            writer.addPage(reader.getPage(page))
    
    with open(output_path, 'wb') as f:
        writer.write(f)


def split_pdf(file_path, output_name):
    pdf = PdfFileReader(file_path)
    for page in range(pdf.getNumPages()):
        writer = PdfFileWriter()
        writer.addPage(pdf.getPage(page))

        output = f"{output_name}_page_{page + 1}.pdf"
        with open(output, 'wb') as f:
            writer.write(f)


def extract_pdf_text(file_path):
    with open(file_path, 'rb') as fin, open('output.txt', 'wb') as fout:
        extract_text_to_fp(fin,fout)   
