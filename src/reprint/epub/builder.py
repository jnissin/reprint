"""EPUB document builder."""

import os
import azure.ai.formrecognizer as fr

from typing import List
from ebooklib import epub
from urlextract import URLExtract

from reprint.azure.converters import table_to_html, paragraph_to_html
from reprint.core.processing import (
    get_document_elements,
    sort_document_elements,
    filter_document_elements
)
from reprint.core.models import DocumentElement
from reprint.utils.text import fix_hyphenation, convert_urls_to_links

from reprint.epub.styles import DEFAULT_EPUB_CSS


def get_title(pdf_file_path: str, result: fr.AnalyzeResult) -> str:
    """Extract document title from analysis result or fallback to filename."""
    for p in result.paragraphs:
        if p.role == "title":
            return p.content.strip()
    return os.path.splitext(os.path.basename(pdf_file_path))[0]


def document_elements_to_epub_html(doc_elements: List[DocumentElement]) -> List[epub.EpubHtml]:
    chapters = []
    current_chapter = None
    current_chapter_content = []

    # Process sorted and filtered document elements
    for de in doc_elements:
        if de.element_type == "paragraph" and de.element.role == "sectionHeading":
            # Start a new chapter
            if current_chapter:
                current_chapter.content = "".join(current_chapter_content)
                chapters.append(current_chapter)
            
            chapter_title = de.element.content.strip()
            heading_level = chapter_title.count(".") + 1
            chapter_filename = f"chapter_{len(chapters)+1}.xhtml"
            current_chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_filename, lang='en')
            current_chapter_content = [f'<h{heading_level}>{chapter_title}</h{heading_level}>']
        elif de.element_type == "paragraph":
            paragraph_html = paragraph_to_html(de.element)
            current_chapter_content.append(paragraph_html)
        elif de.element_type == "table":
            table_html = table_to_html(de.element)
            current_chapter_content.append(table_html)
        else:
            raise ValueError(f"Unknown element type: {de.element_type}")

    # Add the last chapter
    if current_chapter:
        current_chapter.content = "".join(current_chapter_content)
        chapters.append(current_chapter)
    
    return chapters


def postprocess_chapter(chapter: epub.EpubHtml) -> epub.EpubHtml:
    chapter.content = fix_hyphenation(chapter.content)
    extractor = URLExtract()
    chapter.content = convert_urls_to_links(
        text=chapter.content,
        extractor=extractor
    )
    return chapter


def create_epub(
    pdf_file_path: str,
    result: fr.AnalyzeResult,
    epub_css: str = DEFAULT_EPUB_CSS
) -> epub.EpubBook:
    book = epub.EpubBook()
    title = get_title(pdf_file_path=pdf_file_path, result=result)
    book.set_title(title)

    # 1. Create a list of all elements (paragraphs and tables)
    doc_elements = get_document_elements(result)

    # 2. Sort document elements
    doc_elements = sort_document_elements(doc_elements)

    # 3. Filter overlapping document elements
    doc_elements = filter_document_elements(doc_elements)

    # 4. Parse document elements into epub chapters (HTML)
    chapters = document_elements_to_epub_html(doc_elements)

    # 5. Postprocess chapters
    for i in range(len(chapters)):
        chapters[i] = postprocess_chapter(chapters[i])

    # Add the CSS to each chapter
    for chapter in chapters:
        chapter.content = epub_css + chapter.content

    # Add chapters to the book
    for chapter in chapters:
        book.add_item(chapter)

    # Create table of contents
    toc = []
    for chapter in chapters:
        toc.append(epub.Link(chapter.file_name, chapter.title, chapter.id))

    # Set the table of contents and spine
    book.toc = toc
    book.spine = ["nav"] + chapters

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    return book


def save_epub(epub_file_path: str, book: epub.EpubBook):
    epub.write_epub(epub_file_path, book)
