from pathlib import Path
import pytest
from tools.job_scanner import read_job_posting, _validate_public_url


def test_reads_and_limits_local_text(tmp_path):
    job = tmp_path / "job.txt"
    job.write_text("  Python   Developer\nReact  ", encoding="utf-8")
    assert read_job_posting.invoke({"source": str(job)}) == "Python Developer React"


def test_rejects_non_txt_local_file(tmp_path):
    file = tmp_path / "job.pdf"
    file.write_text("not a pdf", encoding="utf-8")
    with pytest.raises(ValueError):
        read_job_posting.invoke({"source": str(file)})


def test_rejects_localhost_url():
    with pytest.raises(ValueError):
        _validate_public_url("http://127.0.0.1/admin")
