from __future__ import annotations

import re
import xml.etree.ElementTree as etree

from markdown import Extension
from markdown.treeprocessors import Treeprocessor


class VlnaTreeprocessor(Treeprocessor):
    def __init__(self, prefixes: str, char: str):
        self.prefixes = prefixes
        self.char = char

        # https://regex101.com/r/M9eVqS/1
        self.RE_INLINE = re.compile(rf"\b([{self.prefixes}])[ ]+(?=\w)", re.MULTILINE)

        # https://regex101.com/r/w86443/4
        self.RE_ENDLINE = re.compile(rf"\b([{self.prefixes}])[ ]*\n[ ]*", re.MULTILINE)

    def run(self, root: etree.Element) -> None:
        self.finder(root)

    def finder(self, root: etree.Element) -> None:
        for child in root:
            if child.text:
                child.text = self.substitude(child.text)
            if child.tail:
                child.tail = self.substitude(child.tail)

            self.finder(child)

    def substitude(self, text: str):
        subst = f"\\g<1>{self.char}"
        inlineChanges = self.RE_INLINE.sub(subst, text, 0)
        endLineChanges = self.RE_ENDLINE.sub(subst, inlineChanges, 0)
        return endLineChanges


class VlnaExtension(Extension):
    """
    Vlna is used to replace spaces between words with non-breaking spaces in Czech language texts.
    https://github.com/JakubAndrysek/vlna/blob/main/vlna.py
    """

    def __init__(self, **kwargs):
        self.config = {
            "char": ["&nbsp;", "Character to replace with."],
            "prefixes": ["AaIiKkSsVvUuOoZz0123456789", "Prefixes between words."],
        }

        """ Default configuration options. """
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        """
        Add `VlnaExtension` to the Markdown instance.
        """
        md.registerExtension(self)

        md.treeprocessors.register(VlnaTreeprocessor(self.getConfig("prefixes"), self.getConfig("char")), "vlna", -1000)


def makeExtension(**kwargs):
    return VlnaExtension(**kwargs)
