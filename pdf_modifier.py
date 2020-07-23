import ntpath
from os import path

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

def rotate_page(file_path, page_number, direction, output_path):
    writer = PdfFileWriter()
    reader = PdfFileReader(file_path)
    for x in range(reader.getNumPages()):
        page = reader.getPage(x)
        if x + 1 == page_number:
            if direction == 'clockwise':
                page.rotateClockwise(90)
            else:
                page.rotateCounterClockwise(90)
        writer.addPage(page)
    
    output_filename = path_leaf(file_path).split('.')[0]
    output = f"{path.join(output_path, output_filename)}_rotated.pdf"
    with open(output, 'wb') as f:
        writer.write(f)


def merge_pdfs(file_paths, output_path='output.pdf'):
    writer = PdfFileWriter()

    for file_path in file_paths:
        reader = PdfFileReader(file_path)
        for page in range(reader.getNumPages()):
            writer.addPage(reader.getPage(page))
    
    with open(output_path, 'wb') as f:
        writer.write(f)


def split_pdf(file_path, output_path):
    pdf = PdfFileReader(file_path)
    for page in range(pdf.getNumPages()):
        writer = PdfFileWriter()
        writer.addPage(pdf.getPage(page))

        output_filename = path_leaf(file_path).split('.')[0]
        output = f"{path.join(output_path, output_filename)}_page_{page + 1}.pdf"
        with open(output, 'wb') as f:
            writer.write(f)


def extract_pdf_text(file_path):
    with open(file_path, 'rb') as fin, open('output.txt', 'wb') as fout:
        extract_text_to_fp(fin,fout)   


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)