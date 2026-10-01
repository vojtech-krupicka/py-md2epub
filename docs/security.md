# Security

Because a manifest and its Markdown are treated as input from a project you may not fully trust (or
may be sharing/collaborating on), md2epub applies several defenses by default rather than as
opt-ins:

- **Markdown extensions are allow-listed.** Only Markdown's own built-ins and `md2epub.extensions.*`
  are enabled unless `--trust-extensions` is passed. An extension is a Python module that gets
  imported and executed, so this isn't optional by default — see
  [`build --trust-extensions`](cli-reference.md#md2epub-build).
- **Rendered chapter HTML is sanitized** before being embedded, via [nh3](https://nh3.readthedocs.io/).
- **Every Jinja template renders sandboxed.** This includes any custom template a manifest points at
  (`type: custom` pages, or `custom_template` overrides) — the sandboxed, auto-escaping environment
  applies to all of them, not just the built-in ones.
- **Every manifest path is contained.** Chapter sources, images, stylesheets, `include_file`, and
  custom templates are all resolved and checked to stay inside the project; none can escape via `..`
  or an absolute path.

None of this makes md2epub safe to point at a fully adversarial, unreviewed manifest without any
other precautions — it means the common ways a manifest or its Markdown could otherwise reach outside
the project (arbitrary Python execution via extensions, template injection, path traversal,
unsanitized HTML) are closed by default, and the one deliberately sharp edge
(`--trust-extensions`) has to be asked for explicitly.
