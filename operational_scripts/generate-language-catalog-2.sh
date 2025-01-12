#!/bin/sh

# Credit:
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n
#
# The pybabel init command takes the messages.pot file as input and writes a new language catalog to the directory given in the -d option for the language specified in the -l option. I'm going to be installing all the translations in the app/translations directory, because that is where Flask-Babel will expect translation files to be by default. The command will create a es subdirectory inside this directory for the Spanish data files. In particular, there will be a new file named app/translations/es/LC_MESSAGES/messages.po, that is where the translations need to be made.

pybabel init -i messages.pot -d ../subscribie/translations/ -l de
