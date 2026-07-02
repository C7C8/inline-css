#  inline-css
#  Copyright (C) 2026 Christopher Myers
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import logging
import pathlib
from typing import List, Any

from lxml import etree
from lxml.etree import ElementTree
from tinycss2 import parse_stylesheet
from tinycss2.ast import QualifiedRule, AtRule

log = logging.getLogger(__name__)


def inline_css_from_files(html: pathlib.Path, css_file_paths: List[pathlib.Path]) -> str:
    """
    Inline CSS stylesheet rules in an HTML document. Wrapper for `inline_css()`
    :param html: Path to an HTML document
    :param css_file_paths: Paths to CSS files
    :return: HTML with CSS styles inlined.
    """

    log.debug("Validating & parsing HTML input file '%s'", html)
    try:
        # noinspection PyTypeChecker
        html_root = etree.parse(html, parser=etree.HTMLParser())
    except:
        log.exception("Failed to parse HTML file '%s': ", html)
        raise

    css_parsed: list[QualifiedRule | AtRule] = []
    for css_file_path in css_file_paths:
        try:
            log.debug("Parsing and validating CSS style sheet '%s'", css_file_path)
            with open(css_file_path, "r") as css_file:
                css_parsed.extend(parse_stylesheet(css_file.read(), skip_comments=True, skip_whitespace=True))
        except:
            log.exception("Failed to parse HTML file '%s'", css_file_path)
            raise

    # This normally throws a warning because WhitespaceToken and CommentToken can be present, but setting skip_comments
    # and skip_whitespace to false above stops those from ever being emitted. Hence, typechecker is wrong here.
    #noinspection PyTypeChecker
    return etree.tostring(inline_css(html_root, css_parsed))


def inline_css(html: ElementTree, rules: List[QualifiedRule | AtRule]) -> ElementTree:
    """
    Inline CSS stylesheet rules in an HTML document. Accepts lxml ElementTrees and cssutils CSSStyleSheet objects.
    :param html: Parsed HTML ElementTree
    :param css_sheets: Parsed CSS style sheets
    :return HTML ElementTree with styles inlined.
    """
    return html


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="inline-css",
        description="Inlines CSS rules within stylesheets and applies them to HTML files"
    )
    parser.add_argument("--verbose", "-v",action="store_true", help="Enable verbose output")
    parser.add_argument("html", type=pathlib.Path, help="Source HTML file")
    parser.add_argument("css", type=pathlib.Path, nargs="+", help="Source CSS files")

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--out", "-o", type=argparse.FileType("w"), help="File to write HTML output to. Will be overwritten if it already exists.")
    output_group.add_argument("--outdir", "-d", type=pathlib.Path, help="Directory to write HTML output to. Filename will be same as the source file.")
    output_group.add_argument("--quash", action="store_true", help="Overwrite the original HTML file with the inlined output. Very dangerous!")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    print(inline_css_from_files(args.html, args.css))
