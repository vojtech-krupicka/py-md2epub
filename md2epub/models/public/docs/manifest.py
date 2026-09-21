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

new_value = {
    "title": "",
    "examples": [],
    "description": (""),
}
