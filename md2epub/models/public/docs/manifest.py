# region Manifest

manifest_title = {
    "title": "The title of the publication",
    "examples": ["Alice in Wonderland"],
    "description": (
        "An `<dc:title>` element. An OPF Package Document must include at least one"
        " instance of this element type, however multiple instances are permitted."
        "\n\nSee: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.1"
    ),
}
manifest_supertitle = {
    "title": "The supertitle of the publication",
    "examples": ["First book"],
    "description": (
        "The supertitle of the publication. This is not really in OPF document or"
        " in specifications and maybe, this will be removed later."
    ),
}
manifest_subtitle = {
    "title": "The subtitle of the publication",
    "examples": ["A tale of wonderland"],
    "description": (
        "The subtitle of the publication. This is not really in OPF document or"
        " in specifications and maybe, this will be removed later."
    ),
}
manifest_language = {
    "title": "A language of the resource",
    "examples": ["en"],
    "description": (
        "Identifies a language of the intellectual content of the Publication."
        " An OPF Package Document must include at least one instance of this element"
        " type, however multiple instances are permitted."
        "\n\nSee: See: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.2"
    ),
}
manifest_created = {
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
manifest_published = {
    "title": "Date of publication",
    "examples": ["2024", "2024-10", "2024-10-03"],
    "description": (
        "Date of publication of the book with same rules and formats as `created`."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.7>"
    ),
}
manifest_modified = {
    "title": "Date of modification",
    "examples": ["2024", "2024-10", "2024-10-03"],
    "description": (
        "Date of modification of the book with same rules and formats as `created`."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.7>"
    ),
}

manifest_file = {
    "title": "Manifest file path",
    "examples": ["book/manifest.yaml"],
    "description": "Filled in automatically from the path the manifest was loaded from; not set by the manifest itself.",
}
manifest_author = {
    "title": "Main author",
    "examples": ["Jane Doe", {"name": "Jane Doe", "role": "aut"}],
    "description": (
        "The book's main author. A plain string is shorthand for `{name: <string>}`."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.2>"
    ),
}
manifest_additional_authors = {
    "title": "Additional authors",
    "examples": [["Jane Doe", "John Smith"]],
    "description": "Co-authors listed after the main `author`, in the same shorthand-or-object form.",
}
manifest_book_id = {
    "title": "Book identifier",
    "examples": [{"value": "978-0-575-08626-5", "scheme": "isbn"}],
    "description": (
        "The book's unique identifier. Left unset, a stable one is derived from the title, author,"
        " publication date and language - the same manifest always gets the same identifier, so"
        " rebuilding it doesn't look like a new book to a reading system."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10>"
    ),
}
manifest_format = {
    "title": "Format",
    "examples": ["application/epub+zip"],
    "description": (
        "The file format, physical medium, or dimensions of the resource."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.9>"
    ),
}
manifest_identifiers = {
    "title": "Additional identifiers",
    "examples": [[{"scheme": "isbn", "value": "978-0-575-08626-5"}]],
    "description": (
        "Further identifiers for the resource (an ISBN, a DOI, ...), in addition to `book_id`."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10>"
    ),
}
manifest_subjects = {
    "title": "Subjects",
    "examples": [["Fantasy", "Adventure"]],
    "description": (
        "Keywords, key phrases or classification codes describing the topic of the resource."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.3>"
    ),
}
manifest_description = {
    "title": "Description",
    "examples": ["A short account of the book."],
    "description": (
        "An abstract, a table of contents, or a free-text account of the resource."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.4>"
    ),
}
manifest_publisher = {
    "title": "Publisher",
    "examples": ["ACME Publishing"],
    "description": (
        "The entity responsible for making the resource available."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.5>"
    ),
}
manifest_contributors = {
    "title": "Contributors",
    "examples": [[{"name": "Ed Itor", "role": "edt"}]],
    "description": (
        "People or organizations whose contribution is secondary to the `author`(s) - editors,"
        " illustrators, translators, and so on."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.6>"
    ),
}
manifest_rights = {
    "title": "Rights",
    "examples": [["Copyright (c) 2026 Jane Doe. All rights reserved."]],
    "description": (
        "Information about rights held in and over the resource."
        "\n\nSee: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.15>"
    ),
}
manifest_calibre = {
    "title": "Calibre metadata",
    "examples": [{"series": "Books of Trinity", "series_index": 1}],
    "description": "Metadata read by Calibre for sorting and for defining a book series and its index within it.",
}
manifest_book = {
    "title": "Book structure",
    "examples": [{"name": "content", "pages": ["text/ch1.md"]}],
    "description": (
        "The book's page structure. All of the manifest's own metadata above is copied onto it"
        " automatically, so it rarely needs to be set here directly."
    ),
}
manifest_config = {
    "title": "Configuration",
    "examples": [{"markdown": {"tab_length": 4}}],
    "description": "Configuration for the EPUB output, the (currently unused) parser, and the Markdown conversion.",
}
