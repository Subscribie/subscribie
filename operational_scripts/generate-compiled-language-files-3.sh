#!/bin/sh

# Credit: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n
# The messages.po file is a sort of source file for translations. When you want to start using these translated texts, this file needs to be compiled into a format that is efficient to be used by the application at run-time. To compile all the translations for the application, you can use the pybabel compile command as follows:


pybabel compile -d ../subscribie/translations/
