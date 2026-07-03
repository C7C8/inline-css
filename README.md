# inline-css

Inline-CSS is a Python module and CLI application for inlining CSS stylesheets by resolving their rules
and applying them directly to the HTML as `style` tags. For example, with the following HTML and CSS:

```html
<div>
    <p class="demo">Hello, world!</p>
</div>
```

```css
.demo {
    color: red;
}
```

The result would be:

```html
<div>
    <p style="color: red">Hello, world!</p>
</div>
```

## Getting Started
This project uses `uv`; running `uv sync` and then `uv run inline_css` ought to do it! See below for usage instructions.

## Usage
```
usage: inline-css [-h] [--verbose] [--out OUT | --outdir OUTDIR | --quash]
                  html css [css ...]

Inlines CSS rules within stylesheets and applies them to HTML files

positional arguments:
  html                  Source HTML file
  css                   Source CSS files

options:
  -h, --help            show this help message and exit
  --verbose, -v         Enable verbose output
  --out OUT, -o OUT     File to write HTML output to. Will be overwritten if
                        it already exists.
  --outdir OUTDIR, -d OUTDIR
                        Directory to write HTML output to. Filename will be
                        same as the source file.
  --quash               Overwrite the original HTML file with the inlined
                        output. Very dangerous!
```

## Limitations

From this library:
* `!important` is not currently respected. Occurrences of `!important` are detected and logged as warnings.
* Existing `style` attributes on HTML tags are quashed by CSS rules.

From consequences of running outside a browser, [these selectors are accepted but never apply:](https://cssselect.readthedocs.io/en/latest/#supported-selectors)
* `:hover`
* `:active`
* `:focus`
* `:target`
* `:visited`

Other limitations:
* [`*:first-of-type`, `*:last-of-type`, `*:nth-of-type`, `*:nth-last-of-type`, `*:only-of-type`. All of these work when you specify an element type, but not with *](https://cssselect.readthedocs.io/en/latest/#supported-selectors)


## *Why?*

If you don't know why you'd need this, you don't need this.

*(There are some content platforms allow custom HTML but don't allow custom stylesheets, despite requiring styling to
be viable. This is to make life easier for content creators on those platforms.)*
