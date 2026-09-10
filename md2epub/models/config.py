from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, model_validator


class Config(BaseModel):
    DATA_DIR: ClassVar[Path] = (Path(__file__).parent / ".." / "data").resolve()
    TEMPLATE_DIR: ClassVar[Path] = (Path(__file__).parent / "templates").resolve()
    WORK_DIR: ClassVar[Path] = Path().resolve()

    epub_suffix: str = ".epub"
    html_suffix: str = ".xhtml"

    def set_work_dir(self, work_dir: str | Path):
        Config.WORK_DIR = Path(work_dir).resolve()

    @model_validator(mode="before")
    @classmethod
    def on_before_model_validate(cls, data: Any) -> Any:
        # if "data_dir" in data:
        #     data["data_dir"] = Path(data["data_dir"]).resolve()
        # if "template_dir" in data:
        #     data["template_dir"] = Path(data["template_dir"]).resolve()
        data.pop("data_dir", None)
        data.pop("template_dir", None)

        return data
