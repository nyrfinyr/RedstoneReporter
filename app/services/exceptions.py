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


class ProjectNotFoundError(ResourceNotFoundError):
    """Project not found."""

    def __init__(self, project_id: int):
        self.project_id = project_id
        super().__init__(f"Project with ID {project_id} not found")


class EpicNotFoundError(ResourceNotFoundError):
    """Epic not found."""

    def __init__(self, epic_id: int):
        self.epic_id = epic_id
        super().__init__(f"Epic with ID {epic_id} not found")


class TestCaseDefinitionNotFoundError(ResourceNotFoundError):
    """Test case definition not found."""

    def __init__(self, definition_id: int):
        self.definition_id = definition_id
        super().__init__(f"TestCaseDefinition with ID {definition_id} not found")


class DeletionConstraintError(ReporterException):
    """Cannot delete resource due to dependent resources."""

    def __init__(self, resource_type: str, resource_id: int, reason: str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"Cannot delete {resource_type} with ID {resource_id}: {reason}")
