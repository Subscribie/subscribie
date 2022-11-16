---
title: "Translation (i18n)"
date: 2022-11-16
weight: 2
description: >
  How to translate Subscribie into different languages & update translations.
---

# Prerequisite


{{% pageinfo %}}
You must run Subscribie, see [running Subscribie locally](https://github.com/Subscribie/subscribie#quickstart-without-docker).
{{% /pageinfo %}}

After Subscribie is set-up locally, you can stop Subscribie (`ctrl + c`) then view the translation commands:

```bash
export FLASK_APP=subscribie
flask translate --help
```

```
Usage: flask translate [OPTIONS] COMMAND [ARGS]...

  Translation and localization commands.

Options:
  --help  Show this message and exit.

Commands:
  compile  Compile all languages.
  init     Initialize a new language.
  update   Update all languages.

```


# Steps to update translations

When new text gets added to Subscribie, it needs to be translated. For example:

Before marked for translation:

```python
@app.route("/new-route")
def my_new_route():
    return "This is my new route"

```

After marked for translation:

```python

from flask_babel import _

@app.route("/new-route")
def my_new_route():
    return _("This is my new route")

```


> *warning* Make sure you didn't miss above, the `_` is a function, from the `flask_babel`
  library. `babel` uses `_` to help *find* all the translatable text.


For more complex translation markets in Jinja2 templates see examples:

- [Babel translate flask jinja2 templates](https://github.com/Subscribie/subscribie/compare/master...194-multilinqual-support#diff-4363b9d6b4af3964b71b83a3e49a465690f132b8227b5aef9c062bdb6aea5a2eR68)
- [How to flask translate python variables using Enum](https://github.com/Subscribie/subscribie/compare/master...194-multilinqual-support#diff-26a4fb09b7b90ccf42d6a13b35d380aebe44be88a5c06e7985bd988bc0349097R505-R817)




The main steps to perform static translation in Subscribie are:

1. Update the code replacing hard-coded strings with the `_` function
2. Running `flask translate update`
3. Edit the updated `.po` file with translations (e.g. `subscribie/subscribie/translations/de/LC_MESSAGES/messages.po`)
3. Running `flask translate compile`, which generates a speed optimised translation file (e.g. `subscribie/subscribie/translations/de/LC_MESSAGES/messages.po`)
4. Test the site `flask run`, commit the changes and raise a pull request.


# Credits

The Subscribie i18n translation process was expedited thanks to [Miguel Grinberg](https://twitter.com/miguelgrinberg) who wrote an article [the-flask-mega-tutorial-part-xiii-i18n-and-l10n](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n), and is the author of [Flask Web Development, 2nd Edition](https://www.oreilly.com/library/view/flask-web-development/9781491991725/)