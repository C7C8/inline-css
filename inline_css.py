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

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="inline-css",
        description="Inlines CSS rules within stylesheets and applies them to HTML files"
    )
    parser.add_argument("--verbose", "-v",action="store_true", help="Enable verbose output")
    parser.add_argument("html", type=argparse.FileType("r"), help="Source HTML file")
    parser.add_argument("css", type=argparse.FileType("r"), nargs="+", help="Source CSS files")

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--out", "-o", type=argparse.FileType("w"), help="File to write HTML output to. Will be overwritten if it already exists.")
    output_group.add_argument("--outdir", "-d", type=pathlib.Path, help="Directory to write HTML output to. Filename will be same as the source file.")
    output_group.add_argument("--quash", action="store_true", help="Overwrite the original HTML file with the inlined output. Very dangerous!")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    logging.info("Debug test")
    logging.warning("Warning test")
