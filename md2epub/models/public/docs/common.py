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
    "description": "The name of the series this book belongs to. Calibre uses it to group books of one series together.",
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
