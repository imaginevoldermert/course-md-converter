from zipfile import ZipFile
import io
from pathlib import Path
import shutil

from cmd_converter.result_files import build_result_zip, list_result_files


def test_result_inventory_and_zip():
    # Use the gitignored output tree because this managed Windows environment
    # denies access to directories created through tempfile/pytest tmp_path.
    result_dir = Path("outputs") / "_test_result_files"
    try:
        (result_dir / "assets").mkdir(parents=True, exist_ok=True)
        (result_dir / "note.md").write_text("# note", encoding="utf-8")
        (result_dir / "assets" / "formula.png").write_bytes(b"png")
        inventory = list_result_files(result_dir)
        assert [item["文件"] for item in inventory] == ["assets/formula.png", "note.md"]
        with ZipFile(io.BytesIO(build_result_zip(result_dir))) as archive:
            assert archive.namelist() == ["assets/formula.png", "note.md"]
    finally:
        shutil.rmtree(result_dir, ignore_errors=True)
