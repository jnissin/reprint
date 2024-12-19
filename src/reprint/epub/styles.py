"""EPUB stylesheet definitions."""

DEFAULT_EPUB_CSS = '''
<style>
    .table-container {
        margin: 1em 0;
        overflow-x: auto;
    }
    
    .epub-table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
    }
    
    .epub-table th, .epub-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    .epub-table th {
        background-color: #f5f5f5;
    }
    
    aside[epub|type='footnote'] {
        font-size: 0.9em;
        color: #666;
        margin: 1em 0;
        padding-left: 1em;
        border-left: 3px solid #ddd;
    }
    
    img {
        max-width: 100%;
        height: auto;
    }
</style>
'''