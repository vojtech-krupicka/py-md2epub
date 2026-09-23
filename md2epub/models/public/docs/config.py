# region EpubConfig

epub_suffix = {
    "title": "Output file suffix",
    "examples": [".epub", ".zip"],
    "description": (
        "The suffix of the built output file. An EPUB is a zip file, so `.zip` is accepted too -"
        " useful for inspecting the raw contents with a regular archive tool."
    ),
}
html_suffix = {
    "title": "HTML file suffix",
    "examples": [".xhtml"],
    "description": "The suffix used for every generated content file inside the EPUB.",
}
epub_folders = {
    "title": "Extra folders",
    "examples": [["styles"]],
    "description": "Folders to include in the built EPUB in addition to whatever the manifest's pages reference.",
}
epub_files = {
    "title": "Extra files",
    "examples": [["images/favicon.png"]],
    "description": "Files to include in the built EPUB in addition to whatever the manifest's pages reference.",
}

# region ParserConfig

parser_placeholder = {
    "title": "Reserved",
    "examples": ["bar"],
    "description": "Placeholder - no parser-level configuration exists yet.",
}

# region MarkdownConfig

tab_length = {
    "title": "Tab length",
    "examples": [4],
    "description": "The number of spaces a tab in the Markdown source is expanded to.",
}
output_format = {
    "title": "Markdown output format",
    "examples": ["xhtml", "html"],
    "description": "The output format Python-Markdown itself renders to, before md2epub's own postprocessing.",
}
additional_extensions = {
    "title": "Additional Markdown extensions",
    "examples": [["toc", "md2epub.extensions.vlna"]],
    "description": (
        "Extensions to use together with md2epub's own defaults. Only Markdown's built-in"
        " extensions and `md2epub.extensions.*` are allowed unless the build explicitly opted in"
        " to trust the manifest with `--trust-extensions` - a manifest is untrusted input, and an"
        " extension is a Python module Markdown will import and run."
    ),
}
extensions_override = {
    "title": "Markdown extensions override",
    "examples": [["fenced_code", "tables"]],
    "description": "Replace md2epub's default extension list entirely instead of adding to it.",
}
extension_configs = {
    "title": "Markdown extension configuration",
    "examples": [{"toc": {"permalink": True}}],
    "description": "Per-extension configuration, passed straight through to Python-Markdown.",
}

# region Config

include_file = {
    "title": "Included config file",
    "examples": ["../shared-config.yaml"],
    "description": (
        "Path to another config file (YAML or JSON) to load first; this manifest's own `config`"
        " values then override whatever the included file set."
    ),
}
includes_files = {
    "title": "Included config files (resolved)",
    "examples": [["../shared-config.yaml"]],
    "description": "Filled in automatically to track every config file that was included, directly or transitively.",
}
config_epub = {
    "title": "EPUB configuration",
    "examples": [{"epub_suffix": ".epub"}],
    "description": "Basic configuration of the built EPUB file itself.",
}
config_parser = {
    "title": "Parser configuration",
    "examples": [{}],
    "description": "Reserved for future use.",
}
config_markdown = {
    "title": "Markdown configuration",
    "examples": [{"tab_length": 4}],
    "description": "Configuration for the Markdown-to-XHTML conversion used for every chapter.",
}
