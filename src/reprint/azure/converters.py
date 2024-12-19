"""Converts Azure Document Intelligence elements to HTML."""

import azure.ai.formrecognizer as fr


def table_to_html(table: fr.DocumentTable) -> str:
    """Convert Azure Document Table to HTML table."""
    table_html = '''
    <div class="table-container">
        <table class="epub-table">
    '''
    
    grid = [[None for _ in range(table.column_count)] for _ in range(table.row_count)]
    
    for cell in table.cells:
        for row in range(cell.row_index, cell.row_index + int(cell.row_span or 1)):
            for col in range(cell.column_index, cell.column_index + int(cell.column_span or 1)):
                grid[row][col] = cell
    
    for row_index, row in enumerate(grid):
        table_html += "<tr>"
        for col_index, cell in enumerate(row):
            if cell is None:
                continue
            if cell.row_index == row_index and cell.column_index == col_index:
                tag = "th" if cell.kind == "columnHeader" else "td"
                attrs = f' rowspan="{cell.row_span}"' if int(cell.row_span or 1) > 1 else ''
                attrs += f' colspan="{cell.column_span}"' if int(cell.column_span or 1) > 1 else ''
                table_html += f'<{tag}{attrs}>{cell.content}</{tag}>'
        table_html += "</tr>"
    
    table_html += '''
        </table>
    </div>
    '''
    return table_html


def paragraph_to_html(paragraph: fr.DocumentParagraph) -> str:
    """Convert Azure Document Paragraph to HTML."""
    if paragraph.role == "title":
        return f"<h1>{paragraph.content}</h1>"
    elif paragraph.role == "sectionHeading":
        return f"<h2>{paragraph.content}</h2>"
    elif paragraph.role == "pageHeader":
        return f"<header>{paragraph.content}</header>"
    elif paragraph.role == "pageFooter" or paragraph.role == "footnote":
        footnote_id = f"fn{hash(paragraph.content) & 0xffffffff}"
        return f'<aside epub:type="footnote" id="{footnote_id}"><p>{paragraph.content}</p></aside>'
    return f"<p>{paragraph.content}</p>"