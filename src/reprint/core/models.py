from dataclasses import dataclass
from typing import Literal, Union

import azure.ai.formrecognizer as fr

@dataclass
class DocumentElement:
    element_type: Literal["paragraph", "table"]
    element: Union[fr.DocumentParagraph, fr.DocumentTable]