# region Identifier

identifier_value = {
    "title": "Identifier's unique value.",
    "examples": ["d4549bba-fae8-4e19-bccb-3910452733a1", "9780575086265"],
    "description": (
        "A string or number used to uniquely identify the resource. An OPF Package Document must"
        " include at least one instance of this element type, however multiple instances are permitted."
    ),
}
identifier_scheme = {
    "title": "Identifier's opf:scheme attribute.",
    "examples": ["uuid", "isbn"],
    "description": (
        "The scheme attribute names the system or authority that generated or assigned the text"
        " contained within the identifier element, for example `ISBN` or `DOI` The values of the scheme"
        " attribute are case sensitive only when the particular scheme requires it."
    ),
}
bookid_id = {
    "title": "Book identifier",
    "examples": ["BookId", "any-string-is-ok"],
    "description": (
        "At least one identifier must have an id specified (the value being of the XML 'ID' data"
        " type), so it can be referenced from the package unique-identifier attribute."
    ),
}

# region Contributor

contributor_role = {
    "title": "Contributor's role",
    "examples": ["aut", "art", "edt", "ill"],
    "description": (
        "Lower-case 3-character long values specifies contributor's role."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.6>"
    ),
}
contributor_name = {
    "title": "Contributor's name",
    "examples": ["Rev. Dr. Martin Luther King Jr."],
    "description": ("Contributor's full name"),
}
contributor_file_as = {
    "title": "Normalized form of the contributor's name",
    "examples": ["King, Martin Luther Jr."],
    "description": (
        "The `file-as` attribute should be used to specify a normalized form of the contents,"
        " suitable for machine processing."
        "\n\nIf this is ommited, it will be filled from contributor's name in format:"
        "\n\n`Surname, Name`, for example `Martin Luther King` will be transformed to"
        "`King, Martin Luther`."
    ),
}

# region Calibre

calibre_title_sort = {
    "title": "Sorting title",
    "examples": ["Story Of All Of Us, The"],
    "description": (
        "Alphabeticaly correct sorting title, for example `The Story Of All of Us`"
        " would be sorted as `Story Of All Of Us, The`."
    ),
}
calibre_series = {
    "title": "Book series title",
    "examples": ["Harry Potter"],
    "description": (
        "The name of the series this book belongs to. Calibre uses it to group books of one series together."
    ),
}
calibre_series_index = {
    "title": "Index within the book series",
    "examples": [1, 2, 3],
    "description": "The position of this book within its `series`, starting from 1. Calibre sorts the series by it.",
}
calibre_author_link_map = {
    "title": "Author name link map",
    "examples": ["{&quot;Rowlingova, Joanne Kathleen&quot;: &quot;&quot;}"],
    "description": (
        "Maps an author name to a link to their page, as a JSON object with HTML-escaped quotes (`&quot;`)."
        " Left empty, it is generated from the main `author` with an empty link, so you rarely need to set it."
    ),
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
included_files = {
    "title": "Included config files (resolved)",
    "examples": [["../shared-config.yaml"]],
    "description": "Filled in automatically to track every config file that was included, directly or transitively.",
}
config_markdown = {
    "title": "Markdown configuration",
    "examples": [{"tab_length": 4}],
    "description": "Configuration for the Markdown-to-XHTML conversion used for every chapter.",
}

# region Metadata

metadata_title = {
    "title": "The title of the publication",
    "examples": ["Alice in Wonderland"],
    "description": (
        "An `<dc:title>` element. An OPF Package Document must include at least one"
        " instance of this element type, however multiple instances are permitted."
        "\n\nSee: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.1"
    ),
}
metadata_supertitle = {
    "title": "The supertitle of the publication",
    "examples": ["First book"],
    "description": (
        "The supertitle of the publication. This is not really in OPF document or"
        " in specifications and maybe, this will be removed later."
    ),
}
metadata_subtitle = {
    "title": "The subtitle of the publication",
    "examples": ["A tale of wonderland"],
    "description": (
        "The subtitle of the publication. This is not really in OPF document or"
        " in specifications and maybe, this will be removed later."
    ),
}
metadata_title_separator = {
    "title": "Title separator",
    "examples": [" - ", ": "],
    "description": "Separator placed between the title and subtitle wherever the two are shown together.",
}

metadata_language = {
    "title": "A language of the resource",
    "examples": ["en"],
    "description": (
        "Identifies a language of the intellectual content of the Publication."
        " An OPF Package Document must include at least one instance of this element"
        " type, however multiple instances are permitted."
        "\n\nSee: See: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.2"
    ),
}
metadata_created = {
    "title": "Date of creation",
    "examples": ["2024", "2024-10", "2024-10-03"],
    "description": (
        "Date of creation, in the format defined by **Date and Time Formats**"
        " at http://www.w3.org/TR/NOTE-datetime and by ISO 8601 on which it is based."
        " In particular, dates without times are represented in the form YYYY[-MM[-DD]]:"
        " a required 4-digit year, an optional 2-digit month, and if the month is given,"
        " an optional 2-digit day of month."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.7>"
    ),
}
metadata_published = {
    "title": "Date of publication",
    "examples": ["2024", "2024-10", "2024-10-03"],
    "description": (
        "Date of publication of the book with same rules and formats as `created`."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.7>"
    ),
}
metadata_modified = {
    "title": "Date of modification",
    "examples": ["2024", "2024-10", "2024-10-03"],
    "description": (
        "Date of modification of the book with same rules and formats as `created`."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.7>"
    ),
}

metadata_author = {
    "title": "Main author",
    "examples": ["Jane Doe", {"name": "Jane Doe", "role": "aut"}],
    "description": (
        "The book's main author. A plain string is shorthand for `{name: <string>}`."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.2>"
    ),
}
metadata_additional_authors = {
    "title": "Additional authors",
    "examples": [["Jane Doe", "John Smith"]],
    "description": "Co-authors listed after the main `author`, in the same shorthand-or-object form.",
}
metadata_book_id = {
    "title": "Book identifier",
    "examples": [{"value": "978-0-575-08626-5", "scheme": "isbn"}],
    "description": (
        "The book's unique identifier. Left unset, a stable one is derived from the title, author,"
        " publication date and language - the same manifest always gets the same identifier, so"
        " rebuilding it doesn't look like a new book to a reading system."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10>"
    ),
}
metadata_format = {
    "title": "Format",
    "examples": ["application/epub+zip"],
    "description": (
        "The file format, physical medium, or dimensions of the resource."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.9>"
    ),
}
metadata_identifiers = {
    "title": "Additional identifiers",
    "examples": [[{"scheme": "isbn", "value": "978-0-575-08626-5"}]],
    "description": (
        "Further identifiers for the resource (an ISBN, a DOI, ...), in addition to `book_id`."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10>"
    ),
}
metadata_subjects = {
    "title": "Subjects",
    "examples": [["Fantasy", "Adventure"]],
    "description": (
        "Keywords, key phrases or classification codes describing the topic of the resource."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.3>"
    ),
}
metadata_description = {
    "title": "Description",
    "examples": ["A short account of the book."],
    "description": (
        "An abstract, a table of contents, or a free-text account of the resource."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.4>"
    ),
}
metadata_publisher = {
    "title": "Publisher",
    "examples": ["ACME Publishing"],
    "description": (
        "The entity responsible for making the resource available."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.5>"
    ),
}
metadata_contributors = {
    "title": "Contributors",
    "examples": [[{"name": "Ed Itor", "role": "edt"}]],
    "description": (
        "People or organizations whose contribution is secondary to the `author`(s) - editors,"
        " illustrators, translators, and so on."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.6>"
    ),
}
metadata_rights = {
    "title": "Rights",
    "examples": [["Copyright (c) 2026 Jane Doe. All rights reserved."]],
    "description": (
        "Information about rights held in and over the resource."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.15>"
    ),
}
metadata_calibre = {
    "title": "Calibre metadata",
    "examples": [{"series": "Books of Trinity", "series_index": 1}],
    "description": "Metadata read by Calibre for sorting and for defining a book series and its index within it.",
}

# region Book


manifest_file = {
    "title": "Book manifest file path",
    "examples": ["book/manifest.yaml"],
    "description": (
        "Filled in automatically from the path the book manifest was loaded from; not set by the manifest itself."
    ),
}

book_config = {
    "title": "Configuration",
    "examples": [{"markdown": {"tab_length": 4}}],
    "description": "Configuration for the EPUB output, the (currently unused) parser, and the Markdown conversion.",
}
book_pages = {
    "title": "Pages",
    "examples": [[{"type": "toc"}, "text/ch1.md"]],
    "description": (
        "The pages that make up this book, in the order they should appear. A plain string is"
        " shorthand for `{type: chapter, source: <string>}`."
    ),
}


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
book_content_toc_title = {
    "title": "Table of contents label",
    "examples": ["Chapter One", "Part One"],
    "description": (
        "Optional label to show in the table of contents instead of the default one - a chapter's"
        " own first heading, a sub-book's `title`, or as a last resort its technical `name`. Only"
        " changes the table of contents entry, not the page's own heading or `<title>`."
    ),
}
book_content_stylesheets = {
    "title": "Stylesheets",
    "examples": [["styles/book.css"]],
    "description": "Stylesheets linked from this content. Inherited by nested content unless overridden.",
}
book_content_stylesheets_overrides = {
    "title": "Stylesheet overrides",
    "examples": [["styles/chapter-only.css"]],
    "description": (
        "Stylesheets that replace, rather than add to, whatever this content would otherwise inherit from its parent."
    ),
}
book_content_files = {
    "title": "Extra files and folders",
    "examples": [["images", "styles/fonts/font.otf"]],
    "description": (
        "Files and folders to include in the EPUB in addition to whatever the pages already"
        " reference, relative to the manifest's folder. A folder is copied recursively."
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
        'Whether this page is marked `linear="no"` in the spine - present in the book, but not'
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
