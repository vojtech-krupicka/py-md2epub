# region BookContent (shared by Book and every Page type)

book_content_name = {
    "title": "Technical name",
    "examples": ["chapter", "part1", "my-page"],
    "description": (
        "Used to build this content's own path inside the EPUB (`content/<name>.xhtml` for a"
        " generated page, or the folder name for a sub-book). Letters, digits, `.`, `_` and `-`"
        " only - not a name made only of dots, so it can never point outside the project."
    ),
}
toc_title = {
    "title": "Table of contents label",
    "examples": ["Chapter One", "Part One"],
    "description": (
        "Optional label to show in the table of contents instead of the default one - a chapter's"
        " own first heading, a sub-book's `title`, or as a last resort its technical `name`. Only"
        " changes the table of contents entry, not the page's own heading or `<title>`."
    ),
}
stylesheets = {
    "title": "Stylesheets",
    "examples": [["styles/book.css"]],
    "description": "Stylesheets linked from this content. Inherited by nested content unless overridden.",
}
stylesheets_overrides = {
    "title": "Stylesheet overrides",
    "examples": [["styles/chapter-only.css"]],
    "description": (
        "Stylesheets that replace, rather than add to, whatever this content would otherwise"
        " inherit from its parent."
    ),
}

# region Page (shared by every concrete page type)

opf_spine_add = {
    "title": "Add to the OPF spine",
    "examples": [True, False],
    "description": (
        "Whether this page is part of the book's linear reading order."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.4>"
    ),
}
opf_spine_aux = {
    "title": "Auxiliary spine item",
    "examples": [True, False],
    "description": (
        "Whether this page is marked `linear=\"no\"` in the spine - present in the book, but not"
        " part of the main linear reading order (e.g. a notes or appendix page)."
    ),
}
opf_guide_type = {
    "title": "OPF guide type",
    "examples": ["cover", "toc", "title-page"],
    "description": (
        "The reference `type` this page gets in the OPF guide, used by reading systems to jump"
        " straight to a cover, table of contents, etc. `None` means the page is not listed in the"
        " guide at all."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.6>"
    ),
}
opf_guide_title = {
    "title": "OPF guide title",
    "examples": ["Cover", "Table of Contents"],
    "description": "The human-readable title for this page's entry in the OPF guide.",
}
add_to_toc = {
    "title": "Add to the table of contents",
    "examples": [True, False],
    "description": "Whether this page gets its own entry in the table of contents (both the NCX and the TOC page).",
}
custom_template = {
    "title": "Custom template",
    "examples": ["templates/my-chapter.xhtml.jinja"],
    "description": (
        "Path to a Jinja template to render this page with, relative to the manifest's folder,"
        " instead of the built-in one for its page type."
    ),
}

# region CoverPage

cover_image = {
    "title": "Cover image",
    "examples": ["images/cover.jpg"],
    "description": "Path to the cover image, relative to the manifest's folder.",
}

# region TitlePage

title_page_images = {
    "title": "Title page images",
    "examples": [["images/logo.png"]],
    "description": "Images shown on the title page, in order, above the book's metadata.",
}
render_title = {
    "title": "Render the title",
    "examples": [True, False],
    "description": "Whether the title page shows the book's title, subtitle and author.",
}
render_metadata = {
    "title": "Render metadata",
    "examples": [True, False],
    "description": "Whether the title page shows the book's publisher, description, rights and identifiers.",
}
additional_content = {
    "title": "Additional content",
    "examples": ["content/title-foreword.md"],
    "description": "Path to a Markdown file whose rendered content is appended to the title page, if given.",
}

# region TocPage

toc_page_title = {
    "title": "Table of contents heading",
    "examples": ["Table of Contents", "Obsah"],
    "description": "The heading shown at the top of the table of contents page itself.",
}
render_links = {
    "title": "Render links",
    "examples": [True, False],
    "description": "Whether table of contents entries are rendered as links to their target page.",
}
render_depth = {
    "title": "Table of contents depth",
    "examples": [1, 2, 3],
    "description": "How many nesting levels of the table of contents are rendered (sub-books count as one level).",
}

# region Chapter

chapter_source = {
    "title": "Chapter source file",
    "examples": ["text/chapter-01.md"],
    "description": (
        "Path to the chapter's Markdown source, relative to the manifest's folder. The chapter's"
        " file inside the EPUB mirrors this same path (with an `.xhtml` extension), so relative"
        " links and images inside the Markdown keep working unchanged."
    ),
}
chapter_sequence = {
    "title": "Chapter sequence",
    "examples": ["default", "1", "intermezzo"],
    "description": "Reserved for future use in ordering or grouping chapters.",
}

# region CustomPage

custom_template_path = {
    "title": "Template",
    "examples": ["templates/my-page.xhtml.jinja"],
    "description": "Path to the Jinja template that renders this page, relative to the manifest's folder.",
}
custom_sources = {
    "title": "Named sources",
    "examples": [{"intro": "content/intro.md"}],
    "description": "Named source files made available to the template, keyed by whatever name the template expects.",
}
custom_values = {
    "title": "Template values",
    "examples": [{"greeting": "Welcome!"}],
    "description": "Arbitrary values passed straight through to the template, keyed by whatever name it expects.",
}

# region SubBook

subbook_book = {
    "title": "Sub-book",
    "examples": [{"name": "part1", "title": "Part One", "pages": ["text/ch1.md"]}],
    "description": (
        "The nested book this page represents. It gets its own table of contents and its pages"
        " live under their own folder, but it shares the root book's metadata unless overridden."
    ),
}

# region Book

book_title_separator = {
    "title": "Title separator",
    "examples": [" - ", ": "],
    "description": "Separator placed between the title and subtitle wherever the two are shown together.",
}
book_files = {
    "title": "Extra files and folders",
    "examples": [["images", "styles/fonts/font.otf"]],
    "description": (
        "Files and folders to include in the EPUB in addition to whatever the pages already"
        " reference, relative to the manifest's folder. A folder is copied recursively."
    ),
}
book_pages = {
    "title": "Pages",
    "examples": [[{"type": "toc"}, "text/ch1.md"]],
    "description": (
        "The pages that make up this book, in the order they should appear. A plain string is"
        " shorthand for `{type: chapter, source: <string>}`."
    ),
}
