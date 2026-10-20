# es-normalizer-py
_Contact data normalization adapted from the Empreinte Sociométrique's normalizers (in Python)_

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/cyrildever/es-normalizer-py)
![GitHub last commit](https://img.shields.io/github/last-commit/cyrildever/es-normalizer-py)
![GitHub issues](https://img.shields.io/github/issues/cyrildever/es-normalizer-py)
![GitHub license](https://img.shields.io/github/license/cyrildever/es-normalizer-py)
![PyPI - Version](https://img.shields.io/pypi/v/es-normalizer-py)

This is the Python port of [es-normalizer](https://github.com/cyrildever/es-normalizer), the TypeScript normalization library for contact data (address, phones, etc.) adapted from [Edgewhere](https://www.edgewhere.fr)'s Empreinte Sociométrique patented normalizers.

### Motivation

When it comes to hashing data, the necessary uniqueness of the source sometimes makes it hard to compare two hashed data, mostly if dealing with postal address. This library helps normalizing any contact data (the postal or e-mail address, the mobile or landline phone number, the title, names or date of birth of an individual) that would feed any hashing algorithm to make hash comparison always trustable.
It's based on the work for the Empreinte Sociométrique&trade; patented by Cyril Dever for Edgewhere.

### TypeScript version

The TypeScript library lives at [cyrildever/es-normalizer](https://github.com/cyrildever/es-normalizer) and is published on npm as `es-normalizer`.
Version 0.2.4 of this port matches its version 2.4.0: both give the same outputs for the same inputs, the test suite of es-normalizer is ported here case by case, and their dictionaries are the same.
An address dictionary key may hold several words (eg. `CENTRE COMMERCIAL`), translated together before the single words, the longest first.

### Usage

```
pip install es-normalizer-py
```

*IMPORTANT*: as of this version, most normalizers are for use on French data.

To get a normalized string, pass the data and a normalizer function to `normalize()`: it returns the normalized string, or `None` when nothing usable is left.
There are currently eleven specific normalizer functions and a generic one:
* `Any`: the generic normalizer should be used if no specific normalizer exists;
* `AddressLine`: pass any address line through it to get a normalized address, eg. `8, rue Henner` becomes `8 RUE HENNER`, and eventually `True` as parameter when trying to normalize a French address line 1 to also transform the title, eg. `Monsieur Cyril Dever` should then become `1 CYRIL DEVER` when passed `True` instead of `MONSIEUR CYRIL DEVER` for the default behaviour;
* `AddressLine6`: the French address line 6 with the department inserted in between the zip code and the city as in the Empreinte Sociométrique implementation (eg. `75009 75 PARIS`);
* `City`: for normalizing city names (it removes any Cedex mention in French address, for instance);
* `CodePostalFrance`: for French zip code;
* `DateOfBirth`: pass a date and up to two parameters: the input format (eg. `YYYY-MM-DD`) and the output format wished (eg. `ISO_DATE`), the default values being respectively the ISO format and the French date format;
* `DepartementFrance`: extract the French departement number (out of a code postal, for instance);
* `Email`: validates the passed e-mail and returns it in lower-case;
* `FirstName`: pass a first name and get a normalized one (it uses an enlarged French dictionay of first names to process it making it possible to pass from `"J.-Louis"` to `"JEAN LOUIS"`);
* `Mobile`: to validate a French mobile phone;
* `PhoneNumber`: to normalize a French phone or fax number in the international format, eg. `+33 (0) 123 456 789`;
* `StreetNumber`: parses the passed field to normalize it the Empreinte Sociométrique&trade;'s way, eg. `1bis` or `1 bis` becomes `1B`;
* `Title`: returns a code depending on the passed string (1 for gentlemen, 2 for ladies, 0 when undefined or unknown).

```python
from es_normalizer import *

print(normalize('#This is any String(). ', Any))
# THIS IS ANY STRING

print(normalize('Monsieur Cyril Dever', AddressLine(True)))
# 1 CYRIL DEVER

print(normalize('24, rué de Maubeuge', AddressLine()))
# 24 RUE MAUBEUGE

print(normalize('75009 .# Paris', AddressLine6()))
# 75009 75 PARIS

print(normalize('75009 .# Paris', AddressLine6(False)))
# 75009 PARIS

print(normalize('Paris Cedex 09', City))
# PARIS

print(normalize('70/12/01', DateOfBirth('YY/MM/DD', FRENCH_DATE)))
# 01/12/1970

print(normalize(' 75009 ', DepartementFrance))
# 75

print(normalize(' Contact@GMAIL.com', Email))
# contact@gmail.com
```

`DateOfBirth` reads dates the way the forgiving parser of [moment.js](https://momentjs.com/) does, which es-normalizer relies on. Both give the same date for an input that fits its format; for an input that does not, eg. a numeric date read with a month name format (`DD MMM YYYY`), the guess of each may differ.

### Tests

```console
$ git clone https://github.com/cyrildever/es-normalizer-py.git
$ cd es-normalizer-py/
$ pip install -e .
$ python3 -m unittest discover
```


### License

This module is distributed under a MIT license. \
See the [LICENSE](LICENSE) file.


<hr />
&copy; 2026 Cyril Dever. All rights reserved.
