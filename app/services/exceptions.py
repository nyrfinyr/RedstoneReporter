"""Custom exceptions for RedstoneReporter services."""


class ReporterException(Exception):
    """Base exception for all reporter errors."""
    pass


class ResourceNotFoundError(ReporterException):
    """Resource does not exist."""
    pass


class RunNotFoundError(ResourceNotFoundError):
    """Test run not found."""

    def __init__(self, run_id: int):
        self.run_id = run_id
        super().__init__(f"Test run with ID {run_id} not found")


class CaseNotFoundError(ResourceNotFoundError):
    """Test case not found."""

    def __init__(self, case_id: int):
        self.case_id = case_id
        super().__init__(f"Test case with ID {case_id} not found")


class InvalidStateError(ReporterException):
    """Invalid state transition attempted."""
    pass


class InvalidStatusTransitionError(InvalidStateError):
    """Invalid status transition for a test run."""

    def __init__(self, current_status: str, attempted_status: str):
        self.current_status = current_status
        self.attempted_status = attempted_status
        super().__init__(
            f"Cannot transition from '{current_status}' to '{attempted_status}'"
        )


class FileUploadError(ReporterException):
    """Error during file upload."""
    pass


class ScreenshotUploadError(FileUploadError):
    """Error during screenshot upload."""

    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(f"Screenshot upload failed: {message}")


class ValidationError(ReporterException):
    """Data validation error."""
    pass


class InvalidTestDataError(ValidationError):
    """Invalid test case data provided."""

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Invalid data for field '{field}': {message}")
