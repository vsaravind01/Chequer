class FileDoesNotExistError(FileNotFoundError):
    """Exception raised when the file does not exist in the store.
    The exception is a subclass of FileNotFoundError.
    """

    def __init__(self, file_name: str, store_name: str):
        """Initialize the exception.

        Parameters
        ----------
        - **file_name**: (str) Name of the file
        - **store_name**: (str) Name of the store

        Returns
        -------
        - **FileDoesNotExistError**: Exception object
        """
        self.message = f"File '{file_name}' does not exist in the store '{store_name}'"
        super().__init__(self.message)
