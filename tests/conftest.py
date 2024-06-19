"""
conftest.py for pytest fixtures and other related aspects.
see: https://docs.pytest.org/en/7.1.x/reference/fixtures.html
"""

import pathlib
import shutil
import subprocess
import pytest


def check_subproc_run_for_nonzero(completed_proc: subprocess.CompletedProcess) -> None:
    """
    Checks subprocess.CompletedProcess for errors and displays stdout
    in a legible way through pytest.
    """

    try:
        # check that the build returns 0 (nothing failed)
        assert completed_proc.returncode == 0
    except Exception as exc:
        # raise the exception with decoded output from linkchecker for readability
        raise Exception(completed_proc.stdout.decode()) from exc


@pytest.fixture()
def jupyter_book_source() -> pathlib.Path:
    """
    Fixture for Jupyter Book content.
    """

    # return the location of the almanack content
    return pathlib.Path("src/book")


@pytest.fixture()
def build_jupyter_book(
    jupyter_book_source: str, tmp_path: pathlib.Path
) -> pathlib.Path:
    """
    Fixture to build Jupyter Book content.

    Note: we use the command line interface for Jupyter Book as this is
    well documented and may have alignment with development tasks.
    """

    # specify a source and target dir for jupyter book content with tests
    jupyter_book_test_source = pathlib.Path(tmp_path / "jupyter-book-test-source")
    jupyter_book_test_target = pathlib.Path(tmp_path / "jupyter-book-test-target")

    jupyter_book_test_target.mkdir()

    # copy the source and add development-only files for testing
    shutil.copytree(jupyter_book_source, jupyter_book_test_source)
    shutil.copy("tests/data/jupyter-book/sandbox.md", jupyter_book_test_source)
    with open(jupyter_book_test_source / "_toc.yml", "a") as tocfile:
        tocfile.write("      - file: sandbox.md")

    # build jupyter book content
    result = subprocess.run(
        [
            "jupyter-book",
            "build",
            jupyter_book_test_source,
            "--path-output",
            jupyter_book_test_target,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    check_subproc_run_for_nonzero(completed_proc=result)

    return jupyter_book_test_target

from almanack.git_parser import main

@pytest.fixture
def repository_paths():
    """
    Fixture to provide the paths to the test repositories.
    """
    # Compute the base path relative to the location of this add_data script
    base_path = pathlib.Path(__file__).resolve().parent

    add_data_path = base_path / "data/almanack/entropy/add_data.py"

    # Run the add_data.py script to create and initialize the repositories
    subprocess.run(["python", str(add_data_path)], check=True)

    repositories = {
        "high_entropy": base_path / "high_entropy",
        "low_entropy": base_path / "low_entropy",
    }

    yield repositories


def test_main(repository_paths):
    all_logs = main(repository_paths)

    # Check that the logs contain entries for both repositories
    assert "high_entropy" in all_logs
    assert "low_entropy" in all_logs

    # Delete the high_entropy and low_entropy directories to sustain repository structure
    for repo_path in repository_paths.values():
        shutil.rmtree(repo_path)
