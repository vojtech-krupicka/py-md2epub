from pathlib import Path


# def toc_href_filter(child: TocItem, item_source: Path | None, base_path: Path) -> str:
#     href = ""
#     source = child.source or item_source
#     if source:
#         href = source.relative_to(base_path, walk_up=True).as_posix()
#         href += f"#{child.id}"

#     return href
