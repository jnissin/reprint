
import azure.ai.formrecognizer as fr

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest


def create_document_analysis_client(endpoint: str, key: str) -> fr.DocumentAnalysisClient:
    return fr.DocumentAnalysisClient(endpoint, AzureKeyCredential(key))


def create_document_intelligence_client(endpoint: str, key: str) -> DocumentIntelligenceClient:
    return DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )


def analyze_document(pdf_file_path: str, client: DocumentIntelligenceClient) -> AnalyzeResult:
    # See: https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/Python(v4.0)/Layout_model/sample_analyze_layout.py
    # This should be able to output figures as well
    # The newer 2024 API version seems to only be available in west europe, central us etc.
    with open(pdf_file_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            AnalyzeDocumentRequest(bytes_source=f.read())
        )
    return poller.result()