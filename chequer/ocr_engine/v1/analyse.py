from typing import List, Optional
from chequer.utils.s3_utils.s3_store import ChequerStore, StoreTypes
from textractor.parsers import response_parser
from textractor.entities.document import Document
import boto3
import os


class TextractEngine:
    """Textract Wrapper"""

    def __init__(self):
        self.textract = boto3.client("textract")
        self.cheque_store = ChequerStore(StoreTypes.CHEQUES)
        self.ocr_store = ChequerStore(StoreTypes.OCR)

        self._default_queries = [
            {"Text": "What is the name of the payee?", "Alias": "payee_name"},
            {"Text": "What is the amount paid? (in numeric)", "Alias": "amount"},
            {"Text": "What is the date of the cheque? (at the top right corner)", "Alias": "date"},
            {"Text": "What is the account number?", "Alias": "account_number"},
            {"Text": "What is the bank name?", "Alias": "bank_name"},
            {"Text": "What is the IFS code?", "Alias": "ifs_code"},
            {
                "Text": "What is the cheque number? The second part of the number at the center bottom of the cheque and it contains 9 digits.",
                "Alias": "cheque_number",
            },
        ]

    def get_payee_name(self, document: Document) -> Optional[str]:
        """Get the payee name from the document.

        Parameters
        ----------
        - **document**: (Document) The textractor Document object.

        Returns
        -------
        - **payee_name**: (str) The name of the payee.
        """
        for query in document.queries:
            if query.alias == "payee_name":
                return query.result

    def get_amount(self, document: Document) -> Optional[str]:
        """Get the amount from the document.

        Parameters
        ----------
        - **document**: (Document) The textractor Document object.

        Returns
        -------
        - **amount**: (str) The amount.
        """
        for query in document.queries:
            if query.alias == "amount":
                return query.result

    def get_date(self, document: Document) -> Optional[str]:
        """Get the date from the document.

        Parameters
        ----------
        - **document**: (Document) The textractor Document object.

        Returns
        -------
        - **date**: (str) The date.
        """
        for query in document.queries:
            if query.alias == "date":
                return query.result

    def get_account_number(self, document: Document) -> Optional[str]:
        """Get the account number from the document.

        Parameters
        ----------
        - **document**: (Document) The textractor Document object.

        Returns
        -------
        - **account_number**: (str) The account number.
        """
        for query in document.queries:
            if query.alias == "account_number":
                return query.result

    def get_bank_name(self, document: Document) -> Optional[str]:
        """Get the bank name from the document.

        Parameters
        ----------
        - **document**: (Document) The textractor Document object.

        Returns
        -------
        - **bank_name**: (str) The bank name.
        """
        for query in document.queries:
            if query.alias == "bank_name":
                return query.result

    def get_ifs_code(self, document: Document) -> Optional[str]:
        """Get the IFS code from the document.

        Parameters
        ----------
        - **document**: (Document) The textractor Document object.

        Returns
        -------
        - **ifs_code**: (str) The IFS code.
        """
        for query in document.queries:
            if query.alias == "ifs_code":
                return query.result

    def get_cheque_number(self, document: Document) -> Optional[str]:
        """Get the cheque number from the document.

        Parameters
        ----------
        - **document**: (Document) The textractor Document object.

        Returns
        -------
        - **cheque_number**: (str) The cheque number.
        """
        for query in document.queries:
            if query.alias == "cheque_number":
                return query.result

    def analyze_document(self, s3_uri, queries: Optional[List] = None) -> Document:
        """Analyzes the text in a document stored in an Amazon S3 bucket.

        Parameters
        ----------
        - **s3_uri**: (str) The URI of the document to be processed.
        - **queries**: (List) List of queries to be processed.

        Returns
        -------
        - **document**: (Document) The textractor Document object.
        """
        if queries is None:
            queries = self._default_queries
        else:
            queries = [{"Text": query} for query in queries]

        s3_key = self.cheque_store.get_storage_path_from_uri(s3_uri)
        response = self.textract.analyze_document(
            Document={"S3Object": {"Bucket": self.cheque_store.bucket_name, "Name": s3_key}},
            FeatureTypes=["QUERIES", "SIGNATURES"],
            Querys=queries,
        )
        document = response_parser.parse(response)
        return document

    def start_analysis_job(self, s3_uri, queries: Optional[List] = None):
        """Starts the asynchronous detection of text in a document stored in an Amazon S3 bucket.

        Parameters
        ----------
        - **s3_uri**: (str) The URI of the document to be processed.
        - **queries**: (List) List of queries to be processed.

        Returns
        -------
        - **response**: (dict) The response from the Textract API.
        """
        if queries is None:
            queries = self._default_queries
        else:
            queries = [{"Text": query} for query in queries]

        s3_key = self.cheque_store.get_storage_path_from_uri(s3_uri)
        response = self.textract.start_document_analysis(
            DocumentLocation={
                "S3Object": {"Bucket": self.cheque_store.bucket_name, "Name": s3_key}
            },
            OutputConfig={
                "S3Bucket": self.ocr_store.bucket_name,
                "S3Prefix": StoreTypes.OCR.value,
            },
            FeatureTypes=["QUERIES", "SIGNATURES"],
            QueriesConfig={"Queries": queries},
        )
        return response
