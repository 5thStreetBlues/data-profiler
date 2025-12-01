"""Tests for the data-profiler CLI."""

import subprocess
import sys

import pytest

from data_profiler import __version__
from data_profiler.cli.main import create_parser, main
from data_profiler.cli.common import ExitCode


class TestCLIHelp:
    """Test CLI help and version options."""

    def test_version_flag(self, capsys) -> None:
        """Test --version flag shows version and exits cleanly."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert __version__ in captured.out

    def test_version_flag_via_subprocess(self) -> None:
        """Test --version flag via subprocess."""
        result = subprocess.run(
            [sys.executable, "-m", "data_profiler.cli.main", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert __version__ in result.stdout

    def test_help_flag_via_subprocess(self) -> None:
        """Test --help flag via subprocess."""
        result = subprocess.run(
            [sys.executable, "-m", "data_profiler.cli.main", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "data-profiler" in result.stdout
        assert "profile" in result.stdout
        assert "group" in result.stdout

    def test_help_short_flag_via_subprocess(self) -> None:
        """Test -h flag via subprocess."""
        result = subprocess.run(
            [sys.executable, "-m", "data_profiler.cli.main", "-h"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "data-profiler" in result.stdout

    def test_profile_help_via_subprocess(self) -> None:
        """Test 'profile --help' shows profile-specific help."""
        result = subprocess.run(
            [sys.executable, "-m", "data_profiler.cli.main", "profile", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "profile" in result.stdout.lower()
        assert "--output" in result.stdout
        assert "--format" in result.stdout

    def test_group_help_via_subprocess(self) -> None:
        """Test 'group --help' shows group-specific help."""
        result = subprocess.run(
            [sys.executable, "-m", "data_profiler.cli.main", "group", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "group" in result.stdout.lower()
        assert "--by" in result.stdout
        assert "--stats" in result.stdout
        assert "--max-groups" in result.stdout


class TestCLIParser:
    """Test CLI argument parsing."""

    def test_create_parser(self) -> None:
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "data-profiler"

    def test_parse_profile_command(self) -> None:
        """Test parsing profile command with arguments."""
        parser = create_parser()
        args = parser.parse_args(["profile", "test.parquet", "--format", "json"])
        assert args.command == "profile"
        assert len(args.paths) == 1
        assert args.format == "json"

    def test_parse_profile_with_output(self) -> None:
        """Test parsing profile command with output option."""
        parser = create_parser()
        args = parser.parse_args(["profile", "data/", "-o", "report.json", "-r"])
        assert args.command == "profile"
        assert args.recursive is True
        assert str(args.output) == "report.json"

    def test_parse_group_command(self) -> None:
        """Test parsing group command with required --by."""
        parser = create_parser()
        args = parser.parse_args(["group", "cars.parquet", "--by", "make,model"])
        assert args.command == "group"
        assert args.by == "make,model"
        assert args.stats == "count"  # default
        assert args.max_groups == 10  # default

    def test_parse_group_with_stats(self) -> None:
        """Test parsing group command with stats option."""
        parser = create_parser()
        args = parser.parse_args([
            "group", "data.parquet",
            "--by", "category",
            "--stats", "basic",
            "--max-groups", "50",
        ])
        assert args.stats == "basic"
        assert args.max_groups == 50

    def test_parse_group_cross_file(self) -> None:
        """Test parsing group command with cross-file option."""
        parser = create_parser()
        args = parser.parse_args([
            "group", "data.parquet",
            "--by", "id",
            "--cross-file",
        ])
        assert args.cross_file is True


class TestCLIExitCodes:
    """Test CLI exit codes."""

    def test_exit_code_values(self) -> None:
        """Test that exit codes have expected values."""
        assert ExitCode.SUCCESS == 0
        assert ExitCode.FAILURE == 1
        assert ExitCode.USAGE_ERROR == 2
        assert ExitCode.FILE_NOT_FOUND == 10
        assert ExitCode.CARDINALITY_WARNING == 13

    def test_no_command_shows_help(self) -> None:
        """Test that running with no arguments shows help."""
        result = main([])
        assert result == ExitCode.SUCCESS

    def test_profile_no_files_returns_usage_error(self) -> None:
        """Test that profile with no files returns usage error."""
        result = main(["profile"])
        assert result == ExitCode.USAGE_ERROR


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_profile_nonexistent_file(self, tmp_path) -> None:
        """Test profiling a non-existent file returns FILE_NOT_FOUND."""
        result = main(["profile", str(tmp_path / "nonexistent.parquet")])
        # Returns FILE_NOT_FOUND for non-existent files
        assert result == ExitCode.FILE_NOT_FOUND

    def test_group_nonexistent_file(self, tmp_path) -> None:
        """Test group command with non-existent file."""
        result = main(["group", str(tmp_path / "nonexistent.parquet"), "--by", "col1"])
        assert result == ExitCode.FILE_NOT_FOUND

    def test_profile_csv_file(self, tmp_path) -> None:
        """Test profiling a CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,300\n")

        result = main(["profile", str(csv_file)])
        assert result == ExitCode.SUCCESS

    def test_profile_csv_with_json_output(self, tmp_path) -> None:
        """Test profiling with JSON output."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n")
        output_file = tmp_path / "report.json"

        result = main(["profile", str(csv_file), "-o", str(output_file), "--format", "json"])
        assert result == ExitCode.SUCCESS
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_profile_csv_with_html_output(self, tmp_path) -> None:
        """Test profiling with HTML output."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n")
        output_file = tmp_path / "report.html"

        result = main(["profile", str(csv_file), "-o", str(output_file), "--format", "html"])
        assert result == ExitCode.SUCCESS
        assert output_file.exists()
        content = output_file.read_text()
        assert "<html" in content  # Matches both <html> and <html lang="en">
        assert "test.csv" in content

    def test_group_csv_file(self, tmp_path) -> None:
        """Test group command on a CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("category,value\nA,100\nA,150\nB,200\nB,250\nB,300\n")

        result = main(["group", str(csv_file), "--by", "category", "--max-groups", "10"])
        assert result == ExitCode.SUCCESS

    def test_group_with_basic_stats(self, tmp_path) -> None:
        """Test group command with basic stats."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("category,value\nA,100\nA,150\nB,200\nB,250\nB,300\n")

        result = main([
            "group", str(csv_file),
            "--by", "category",
            "--stats", "basic",
            "--max-groups", "10",
        ])
        assert result == ExitCode.SUCCESS

    def test_group_cardinality_warning(self, tmp_path) -> None:
        """Test group command warns on high cardinality."""
        csv_file = tmp_path / "test.csv"
        # Create 20 unique values, max_groups set to 5
        lines = ["id,value"] + [f"{i},{i*100}" for i in range(20)]
        csv_file.write_text("\n".join(lines))

        result = main(["group", str(csv_file), "--by", "id", "--max-groups", "5"])
        assert result == ExitCode.CARDINALITY_WARNING

    def test_profile_directory(self, tmp_path) -> None:
        """Test profiling a directory."""
        # Create some CSV files
        (tmp_path / "file1.csv").write_text("id,value\n1,100\n2,200\n")
        (tmp_path / "file2.csv").write_text("id,value\n3,300\n4,400\n")

        result = main(["profile", str(tmp_path)])
        assert result == ExitCode.SUCCESS
