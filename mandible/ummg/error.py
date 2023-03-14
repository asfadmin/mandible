class UmmgFileNotFound(Exception):
    def __init__(self, file_type: str) -> None:
        self.file_type = file_type

    def __str__(self) -> str:
        return f"{self.file_type} file not found in product files"
