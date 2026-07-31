from typing import List, Optional
from pydantic import Field
from datetime import datetime

import PyPDF2

from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class PDFExtractorToolInputSchema(BaseIOSchema):
    """
    Tool for extracting content from PDF documents.
    Returns the text content of the PDF.
    """

    file_path: str = Field(..., description="Path to the PDF file to extract content from.")
    pages: Optional[List[int]] = Field(None, description="Specific page numbers to extract (1-indexed). If None, extracts all pages.")


#################
# OUTPUT SCHEMA #
#################
class PDFMetadata(BaseIOSchema):
    """Schema for PDF document metadata."""

    title: Optional[str] = Field(None, description="The title of the PDF document if available.")
    author: Optional[str] = Field(None, description="The author of the PDF document if available.")
    created_date: Optional[datetime] = Field(None, description="The creation date of the document if available.")
    num_pages: int = Field(..., description="The total number of pages in the document.")


class PDFExtractorToolOutputSchema(BaseIOSchema):
    """
    Output schema for the PDFExtractorTool. Contains the extracted text and metadata.
    """

    content: str = Field(..., description="Extracted text content from the PDF.")
    pages_extracted: List[int] = Field(..., description="Page numbers that were extracted (1-indexed).")
    metadata: PDFMetadata = Field(..., description="Metadata of the PDF document.")


#################
# CONFIGURATION #
#################
class PDFExtractorToolConfig(BaseToolConfig):
    """Configuration for the PDFExtractorTool."""


#####################
# MAIN TOOL & LOGIC #
#####################
class PDFExtractorTool(BaseTool):
    """
    Tool for extracting text content from PDF documents.

    Attributes:
        input_schema (PDFExtractorToolInputSchema): The schema for the input data.
        output_schema (PDFExtractorToolOutputSchema): The schema for the output data.
    """

    input_schema = PDFExtractorToolInputSchema
    output_schema = PDFExtractorToolOutputSchema

    def __init__(self, config: Optional[PDFExtractorToolConfig] = None):
        """
        Initializes the PDFExtractorTool.

        Args:
            config (Optional[PDFExtractorToolConfig]): Configuration for the tool.
                Defaults to a fresh `PDFExtractorToolConfig()`. It is built here
                rather than in the signature so the default is not one shared,
                mutable instance for the lifetime of the process.
        """
        super().__init__(config or PDFExtractorToolConfig())

    def run(self, params: PDFExtractorToolInputSchema) -> PDFExtractorToolOutputSchema:
        """
        Runs the PDFExtractorTool with the given parameters.

        Args:
            params (PDFExtractorToolInputSchema): The input parameters for the tool.

        Returns:
            PDFExtractorToolOutputSchema: The output of the tool with extracted content.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If `pages` names no page that exists in the document.
            RuntimeError: If the file exists but cannot be parsed as a PDF.
        """
        try:
            with open(params.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get total number of pages
                total_pages = len(pdf_reader.pages)
                
                # Determine which pages to extract
                if params.pages:
                    # Convert 1-indexed page numbers to 0-indexed
                    pages_to_extract = [p-1 for p in params.pages if 0 < p <= total_pages]
                    if not pages_to_extract:
                        raise ValueError(f"No valid pages specified. Document has {total_pages} pages.")
                else:
                    # Extract all pages
                    pages_to_extract = list(range(total_pages))
                
                # Extract text from specified pages
                extracted_text = []
                for page_num in pages_to_extract:
                    page = pdf_reader.pages[page_num]
                    extracted_text.append(page.extract_text())
                
                # Get metadata
                metadata = self.extract_metadata(pdf_reader)
                
                return PDFExtractorToolOutputSchema(
                    content="\n\n".join(extracted_text),
                    pages_extracted=[p+1 for p in pages_to_extract],  # Convert back to 1-indexed
                    metadata=metadata
                )
                
        except (FileNotFoundError, ValueError):
            # A missing file and an out-of-range page selection are both callable
            # errors, not tool failures. Flattening them into a bare `Exception`
            # left callers unable to tell them apart from a corrupt PDF.
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to extract content from PDF: {params.file_path}") from exc

    def extract_metadata(self, pdf_reader: PyPDF2.PdfReader) -> PDFMetadata:
        """
        Extracts metadata from a PDF document.

        Args:
            pdf_reader (PyPDF2.PdfReader): The PDF reader object.

        Returns:
            PDFMetadata: The extracted metadata.
        """
        info = pdf_reader.metadata
        
        # Convert PDF date format to datetime if present
        created_date = None
        if info and '/CreationDate' in info:
            try:
                # PDF dates are often in format: D:YYYYMMDDHHmmSS
                date_str = info['/CreationDate']
                if date_str.startswith('D:'):
                    date_str = date_str[2:]  # Remove 'D:' prefix
                    if len(date_str) >= 14:
                        created_date = datetime(
                            year=int(date_str[0:4]),
                            month=int(date_str[4:6]),
                            day=int(date_str[6:8]),
                            hour=int(date_str[8:10]),
                            minute=int(date_str[10:12]),
                            second=int(date_str[12:14])
                        )
            except (ValueError, IndexError):
                created_date = None
        
        return PDFMetadata(
            title=info.title if info and info.title else None,
            author=info.author if info and info.author else None,
            created_date=created_date,
            num_pages=len(pdf_reader.pages)
        )