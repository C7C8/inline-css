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

## *Why?*

If you don't know why you'd need this, you don't need this.

*(There are some content platforms allow custom HTML but don't allow custom stylesheets, despite requiring styling to
be viable. This is to make life easier for content creators on those platforms.)*
