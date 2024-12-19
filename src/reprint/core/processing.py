"""Core document processing functions."""

import azure.ai.formrecognizer as fr

from typing import List, Dict, Union

from reprint.core.models import DocumentElement
from reprint.utils.geometry import bounding_regions_intersect


def get_document_elements(result: fr.AnalyzeResult) -> List[DocumentElement]:
    """Extract all document elements from analysis result."""
    elements = []
    for paragraph in result.paragraphs:
        elements.append(DocumentElement(element_type="paragraph", element=paragraph))
    for table in result.tables:
        elements.append(DocumentElement(element_type="table", element=table))
    return elements


def get_element_types_by_page(
    doc_elements: List[DocumentElement]
) -> Dict[str, Dict[int, List[Union[fr.DocumentParagraph, fr.DocumentTable]]]]:
    """Group document elements by type and page number."""
    element_types_by_page = {}

    for de in doc_elements:
        if de.element_type not in element_types_by_page:
            element_types_by_page[de.element_type] = {}

        element_type_by_page = element_types_by_page[de.element_type]
        page_number = de.element.bounding_regions[0].page_number
        
        if page_number not in element_type_by_page:
            element_type_by_page[page_number] = []
        
        element_type_by_page[page_number].append(de.element)
    
    return element_types_by_page


def sort_document_elements(doc_elements: List[DocumentElement]) -> List[DocumentElement]:
    """Sort document elements by their position on the page."""
    element_types_by_page = get_element_types_by_page(doc_elements)
    paragraphs_by_page = element_types_by_page["paragraph"]
    tables_by_page = element_types_by_page["table"]

    rearranged_doc_elements = []

    for page_number in sorted(set(paragraphs_by_page.keys()) | set(tables_by_page.keys())):
        page_paragraphs = paragraphs_by_page.get(page_number, [])
        page_tables = tables_by_page.get(page_number, [])
        
        for table in page_tables:
            table_inserted = False
            for i, paragraph in enumerate(page_paragraphs):
                if bounding_regions_intersect(paragraph.bounding_regions[0], table.bounding_regions[0]):
                    rearranged_doc_elements.append(
                        DocumentElement(element_type="table", element=table)
                    )
                    rearranged_doc_elements.extend([
                        DocumentElement(element_type="paragraph", element=p)
                        for p in page_paragraphs[i:]
                    ])
                    page_paragraphs = page_paragraphs[:i]
                    table_inserted = True
                    break
            if not table_inserted:
                rearranged_doc_elements.append(
                    DocumentElement(element_type="table", element=table)
                )
        
        rearranged_doc_elements.extend([
            DocumentElement(element_type="paragraph", element=p)
            for p in page_paragraphs
        ])
    
    return rearranged_doc_elements


def filter_document_elements(doc_elements: List[DocumentElement]) -> List[DocumentElement]:
    """Filter out overlapping document elements."""
    element_types_by_page = get_element_types_by_page(doc_elements)
    tables_by_page = element_types_by_page["table"]

    return [
        de for de in doc_elements
        if not (
            de.element_type == "paragraph"
            and any(
                bounding_regions_intersect(
                    de.element.bounding_regions[0],
                    table.bounding_regions[0]
                )
                for table in tables_by_page.get(
                    de.element.bounding_regions[0].page_number, []
                )
            )
        )
    ]