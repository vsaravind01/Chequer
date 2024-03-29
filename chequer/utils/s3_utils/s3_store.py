from distutils.command import check
import os
from enum import Enum
from typing import IO, Union

import boto3

from chequer.utils.s3_utils.exceptions import FileDoesNotExistError


class StoreTypes(Enum):
    """Enum class to define the types of stores.

    Attributes
    ----------
    - **CHEQUES**: (str) Cheques store - images
    - **OCR**: (str) OCR store - json files
    """

    CHEQUES = "cheques"
    OCR = "ocr"
    SIGNATURES = "signatures"


def check_file_exists(method):
    """Decorator to check if the file exists in the S3 bucket.

    Parameters
    ----------
    - **method**: (function) Method to decorate

    Returns
    -------
    - **function**: Decorated method
    """

    def wrapper(self: "ChequerStore", file_name, *args, **kwargs):
        if not self.file_exists(file_name):
            raise FileDoesNotExistError(file_name, self.store_name)
        return method(self, file_name, *args, **kwargs)

    return wrapper

class ChequerStore:
    """Chequer class to store the S3 bucket name and the S3 client.

    Attributes
    ----------
    - **s3**: (boto3.client) S3 client
    - **bucket_name**: (str) S3 bucket name
    """

    def __init__(self, store_type: StoreTypes):
        _session = boto3.Session()
        self.s3 = _session.client("s3")
        self.bucket_name = os.environ["S3_CHEQUER_STORE"]
        self.store_name = store_type.value

    def get_storage_path_from_uri(self, file_uri: str):
        """Get the storage path from the S3 URI.

        Parameters
        ----------
        - **file_uri**: (str) S3 URI of the file

        Returns
        -------
        - **str**: Storage path of the file
        """
        return file_uri.split("s3://")[1]

    def list_files(self):
        """List all the files in the S3 bucket.

        Returns
        -------
        - **List[str]**: List of file names
        """
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=self.store_name)
        return [content["Key"] for content in response.get("Contents", [])]

    def upload_file(self, file: Union[bytes, str, IO], file_name: str) -> str:
        """Upload a file to the S3 bucket.

        Parameters
        ----------
        - **file**: (bytes) File content
        - **file_name**: (str) Name of the file

        Returns
        -------
        - **str**: S3 URI of the uploaded file
        """
        if self.file_exists(file_name):
            raise FileExistsError
        if isinstance(file, str):
            file = file.encode("utf-8")
        self.s3.put_object(Bucket=self.bucket_name, Key=f"{self.store_name}/{file_name}", Body=file)
        return f"s3://{self.bucket_name}/{self.store_name}/{file_name}"

    def download_file(self, file_name: str, file_path: str):
        """Download a file from the S3 bucket.

        Parameters
        ----------
        - **file_name**: (str) Name of the file
        - **file_path**: (str) Path to save the downloaded file
        """
        if not self.file_exists(file_name):
            raise FileDoesNotExistError(file_name, self.store_name)
        self.s3.download_file(self.bucket_name, f"{self.store_name}/{file_name}", file_path)

    def get_file(self, file_name: str):
        """Get a file from the S3 bucket.

        Parameters
        ----------
        - **file_name**: (str) Name of the file

        Returns
        -------
        - **bytes**: File content
        """
        if not self.file_exists(file_name):
            raise FileDoesNotExistError(file_name, self.store_name)
        response = self.s3.get_object(Bucket=self.bucket_name, Key=f"{self.store_name}/{file_name}")
        return response["Body"].read()

    def delete_file(self, file_name: str):
        """Delete a file from the S3 bucket.

        Parameters
        ----------
        - **file_name**: (str) Name of the file
        """
        if not self.file_exists(file_name):
            raise FileDoesNotExistError(file_name, self.store_name)
        self.s3.delete_object(Bucket=self.bucket_name, Key=f"{self.store_name}/{file_name}")

    def get_file_url(self, file_name: str):
        """Get the URL of a file in the S3 bucket.

        Parameters
        ----------
        - **file_name**: (str) Name of the file

        Returns
        -------
        - **str**: URL of the file
        """
        if not self.file_exists(file_name):
            raise FileDoesNotExistError(file_name, self.store_name)
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": f"{self.store_name}/{file_name}"},
            ExpiresIn=120,
        )

    def get_file_from_uri(self, file_uri: str):
        """Get the file object from the S3 URI.

        Parameters
        ----------
        - **file_uri**: (str) S3 URI of the file

        Returns
        -------
        - **bytes**: File content
        """
        bucket_name, key = file_uri.split("s3://")[1].split("/")
        response = self.s3.get_object(Bucket=bucket_name, Key=key)
        return response["Body"].read()

    def file_exists(self, file_name: str):
        """Check if a file exists in the S3 bucket.

        Parameters
        ----------
        - **file_name**: (str) Name of the file

        Returns
        -------
        - **bool**: True if the file exists, False otherwise
        """
        print(f"{self.store_name}/{file_name}")
        response = self.s3.list_objects_v2(
            Bucket=self.bucket_name, Prefix=f"{self.store_name}/{file_name}", MaxKeys=1
        )
        return "Contents" in response
