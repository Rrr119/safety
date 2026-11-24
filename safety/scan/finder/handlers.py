from abc import ABC, abstractmethod
import os
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Dict, List, Optional

from safety_schemas.models import Ecosystem, FileType


NOT_IMPLEMENTED = "You should implement this."

if TYPE_CHECKING:
    from safety.auth.models import Auth


class FileHandler(ABC):
    """
    Abstract base class for file handlers that define how to handle specific types of files
    within an ecosystem.
    """

    def __init__(self) -> None:
        self.ecosystem: Optional[Ecosystem] = None

    def can_handle(
        self, root: str, file_name: str, include_files: Dict[FileType, List[Path]]
    ) -> Optional[FileType]:
        """
        Determines if the handler can handle the given file based on its type and inclusion criteria.

        Args:
            root (str): The root directory of the file.
            file_name (str): The name of the file.
            include_files (Dict[FileType, List[Path]]): Dictionary of file types and their paths to include.

        Returns:
            Optional[FileType]: The type of the file if it can be handled, otherwise None.
        """
        # Keeping it simple for now

        if not self.ecosystem:
            return None

        for f_type in self.ecosystem.file_types:
            if f_type in include_files:
                current = Path(root, file_name).resolve()
                paths = [
                    p.resolve() if p.is_absolute() else (root / p).resolve()
                    for p in include_files[f_type]
                ]
                if current in paths:
                    return f_type

            # Let's compare by name only for now
            # We can put heavier logic here, but for speed reasons,
            # right now is very basic, we will improve this later.
            # Custom matching per File Type
            if file_name.lower().endswith(f_type.value.lower()):
                return f_type

        return None

    @abstractmethod
    def download_required_assets(
        self,
        auth: "Auth",
        db: Optional[str] = None,
        index_url: Optional[str] = None,
        offline: bool = False,
    ) -> None:
        """
        Abstract method to download required assets for handling files. Should be implemented
        by subclasses.

        Args:
            auth: The authentication object for making authenticated requests.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)


class PythonFileHandler(FileHandler):
    """
    Handler for Python files within the Python ecosystem.
    """

    # Example of a Python File Handler

    def __init__(self) -> None:
        super().__init__()
        self.ecosystem = Ecosystem.PYTHON

    def download_required_assets(
        self,
        auth: "Auth",
        db: Optional[str] = None,
        index_url: Optional[str] = None,
        offline: bool = False,
    ) -> None:
        """
        Downloads the required assets for handling Python files, specifically the Safety database.

        Args:
            auth: The authentication object
        """
        from safety.safety import fetch_database

        db = db or os.getenv("SAFETY_DB_DIR")
        database_source = db if db else False

        # Fetch both the full and partial Safety databases
        fetch_database(
            auth=auth,
            full=False,
            db=database_source,
            cached=True,
            telemetry=True,
            ecosystem=Ecosystem.PYTHON,
            from_cache=False,
            index_url=index_url,
            offline=offline,
        )

        fetch_database(
            auth=auth,
            full=True,
            db=database_source,
            cached=True,
            telemetry=True,
            ecosystem=Ecosystem.PYTHON,
            from_cache=False,
            index_url=index_url,
            offline=offline,
        )


class SafetyProjectFileHandler(FileHandler):
    """
    Handler for Safety project files within the Safety project ecosystem.
    """

    # Example of a Python File Handler

    def __init__(self) -> None:
        super().__init__()
        self.ecosystem = Ecosystem.SAFETY_PROJECT

    def download_required_assets(
        self,
        auth: "Auth",
        db: Optional[str] = None,
        index_url: Optional[str] = None,
        offline: bool = False,
    ) -> None:
        """
        No required assets to download for Safety project files.
        """
        pass


# Mapping of ecosystems to their corresponding file handlers
ECOSYSTEM_HANDLER_MAPPING = MappingProxyType(
    {
        Ecosystem.PYTHON: PythonFileHandler,
        Ecosystem.SAFETY_PROJECT: SafetyProjectFileHandler,
    }
)
