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
from functools import cmp_to_key
from operator import attrgetter
from typing import List, Any, Dict, Tuple, NamedTuple

import lxml
from cssselect import HTMLTranslator, SelectorError
from lxml import etree
from lxml.etree import ElementTree
from src import SpecificityCalculator, Specificity
from tinycss2 import parse_stylesheet, parse_blocks_contents
from tinycss2.ast import QualifiedRule, AtRule, Declaration, WhitespaceToken, HashToken

log = logging.getLogger(__name__)

class _DeclarationsAndSpecificity(NamedTuple):
    declarations: Dict[str, str]
    specificity: Specificity


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
    return etree.tostring(inline_css(html_root, css_parsed), pretty_print=True).decode()


def inline_css(html: ElementTree, rules: List[QualifiedRule | AtRule]) -> ElementTree:
    """
    Inline CSS stylesheet rules in an HTML document. Accepts lxml ElementTrees and cssutils CSSStyleSheet objects.
    :param html: Parsed HTML ElementTree
    :param rules: List of rules in CSS, either QualifiedRule or AtRule (or any combination thereof)
    :return HTML ElementTree with styles inlined.
    """
    # HLD: This works by first identifying all rules that could apply to an element, then applying those rules in
    # appropriate order based on their CSS specificity. All styled elements have to be identified first in order to
    # build up an appropriate sorting order for specificity.

    # Part 1: For every CSS declaration, find the matching elements and build up a dictionary of them to the list of
    # rules that could apply to them, plus their specificity.
    el_declaration_mappings: Dict[lxml.etree.Element, List[_DeclarationsAndSpecificity]] = {}
    selector_translator = HTMLTranslator()
    for rule in rules:
        selector = rule.serialize().split("{")[0].strip()

        # Map out declarations properly into a dictionary. This will be used later when calculating style rules.
        declarations: Dict[str, str] = {
            declaration_raw.name: declaration_raw.serialize().removeprefix(f"{declaration_raw.name}:").strip()
            for declaration_raw in parse_blocks_contents(rule.content, skip_comments=True, skip_whitespace=True)
        }

        # Check for #important; we have no way to handle this at the moment.
        if any(map(lambda value: "!important" in value, declarations.values())):
            log.warning("Selector '%s' contains a !important rule; these are not respected!")

        try:
            xpath = selector_translator.css_to_xpath(selector)
        except SelectorError as e:
            # TODO add CLI option for enabling/disabling bad selector skipping
            log.warning("Selector '%s' failed to translate to xpath and is SKIPPED", selector, exc_info=e)
            continue
        specificity = SpecificityCalculator.calculate(selector)
        selected_elements = html.xpath(xpath)
        log.debug("Translated CSS selector '%s', (%d matches, specificity %s) to HTML Xpath selector '%s'", selector, len(selected_elements), specificity, xpath)

        # Apply this selector + ruleset to each element this selector matches
        declarations_w_specificity = _DeclarationsAndSpecificity(declarations, specificity)
        for element in selected_elements:
            if element not in el_declaration_mappings:
                el_declaration_mappings[element] = []
            el_declaration_mappings[element].append(declarations_w_specificity)

    log.debug("CSS selection pass finished, identified %d element-to-declaration mappings. Applying styles...", len(el_declaration_mappings))

    # Part 2: For each element, sort the list of declarations by CSS specificity. Then, apply each set of rules to the
    # HTML element's `style` attribute.
    for element, declarations_for_element in el_declaration_mappings.items():
        declarations_for_element.sort(key=attrgetter("specificity"))

        # This bit of magic condenses all styles in the list of declarations into a set with no duplicates. Since higher
        # ranking declarations are last in declarations_for_element, the final outcome has the styles from the most
        # specific CSS selectors taking priority. Neato!
        style_dict: Dict[str, str] = {}
        for declaration in declarations_for_element:
            style_dict.update(declaration.declarations)

        # Assemble and format the final style string to be applied to our element
        style_str = "; ".join(list(map(lambda item: f"{item[0]}: {item[1]}", style_dict.items())))
        log.debug("Applying style '%s' to element '%s'", style_str, element.tag)
        element.attrib["style"] = style_str

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
