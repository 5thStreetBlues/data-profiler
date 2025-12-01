"""Base formatter interface for output formatters.

This module defines the abstract base class for all output formatters,
establishing a consistent interface for formatting profiling results.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data_profiler.models.profile import FileProfile, DatasetProfile
    from data_profiler.models.grouping import GroupingResult
    from data_profiler.models.relationships import RelationshipGraph


class BaseFormatter(ABC):
    """Abstract base class for output formatters.

    All formatters must implement methods for formatting different
    types of profiling results (file profiles, dataset profiles,
    grouping results, and relationship graphs).
    """

    @abstractmethod
    def format_file_profile(self, profile: FileProfile) -> str:
        """Format a file profile as a string.

        Args:
            profile: FileProfile to format.

        Returns:
            Formatted string representation.
        """
        pass

    @abstractmethod
    def format_dataset_profile(self, profile: DatasetProfile) -> str:
        """Format a dataset profile as a string.

        Args:
            profile: DatasetProfile to format.

        Returns:
            Formatted string representation.
        """
        pass

    @abstractmethod
    def format_grouping_result(self, result: GroupingResult) -> str:
        """Format a grouping result as a string.

        Args:
            result: GroupingResult to format.

        Returns:
            Formatted string representation.
        """
        pass

    def format_relationship_graph(self, graph: RelationshipGraph) -> str:
        """Format a relationship graph as a string.

        Args:
            graph: RelationshipGraph to format.

        Returns:
            Formatted string representation.
        """
        # Default implementation - subclasses can override
        return ""

    def write(
        self,
        content: str,
        path: Path,
    ) -> None:
        """Write formatted content to a file.

        Args:
            content: Formatted content string.
            path: Output file path.
        """
        path.write_text(content, encoding="utf-8")

    def write_file_profile(
        self,
        profile: FileProfile,
        path: Path,
    ) -> None:
        """Format and write a file profile to a file.

        Args:
            profile: FileProfile to format and write.
            path: Output file path.
        """
        content = self.format_file_profile(profile)
        self.write(content, path)

    def write_dataset_profile(
        self,
        profile: DatasetProfile,
        path: Path,
    ) -> None:
        """Format and write a dataset profile to a file.

        Args:
            profile: DatasetProfile to format and write.
            path: Output file path.
        """
        content = self.format_dataset_profile(profile)
        self.write(content, path)

    def write_grouping_result(
        self,
        result: GroupingResult,
        path: Path,
    ) -> None:
        """Format and write a grouping result to a file.

        Args:
            result: GroupingResult to format and write.
            path: Output file path.
        """
        content = self.format_grouping_result(result)
        self.write(content, path)
