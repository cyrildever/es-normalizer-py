"""
The test suite of es-normalizer (`test/src/typescript/node.spec.ts`), case by case: both libraries must give the same outputs
"""

from unittest import TestCase

from es_normalizer import (
    FRENCH_DATE,
    ISO_DATE,
    AddressLine,
    AddressLine6,
    Any,
    City,
    CodePostalFrance,
    DateOfBirth,
    DepartementFrance,
    Email,
    FirstName,
    Milliseconds,
    Mobile,
    PhoneNumber,
    StreetNumber,
    Timestamp,
    Title,
    normalize,
    uniformize,
)


class TestUniformize(TestCase):
    def test_dismiss_any_weird_character(self):
        self.assertEqual(uniformize(" cAfé#@~eT*%chocolAT )"), "CAFE ET CHOCOLAT")
        self.assertEqual(uniformize("Bœuf Lætitia ŒUVRE"), "BOEUF LAETITIA OEUVRE")
        self.assertEqual(uniformize("Albert 1ᵉʳ, Mᵐᵉ"), "ALBERT 1ER MME")
        self.assertEqual(uniformize("ﬁlature ﬂeurie"), "FILATURE FLEURIE")
        self.assertEqual(uniformize("Ｒｕｅ"), "RUE")
        self.assertEqual(uniformize("Nº 12"), "N 12")
        self.assertEqual(uniformize("№ 12"), "N 12")
        self.assertEqual(uniformize("N° 12"), "N 12")


class TestAddressLine(TestCase):
    def test_any_type_of_address_line(self):
        # French address line 1
        self.assertEqual(normalize("Mr Jean Martin", AddressLine()), "MR JEAN MARTIN")
        self.assertEqual(normalize("Mr Jean Martin", AddressLine(True)), "1 JEAN MARTIN")
        # French address line 2
        self.assertEqual(normalize("c/o Mr et Mme Dupont", AddressLine()), "C O MR MME DUPONT")
        # French address line 3
        self.assertEqual(normalize("Bât. 4, escalier G", AddressLine()), "BAT 4 ESC G")
        # French address line 4
        self.assertEqual(normalize("128 r du Faubourg Saint Honoré ", AddressLine()), "128 RUE FBG ST HONORE")
        self.assertEqual(normalize("*** rue \nHenner", AddressLine()), "RUE HENNER")
        self.assertIsNone(normalize("$µ%*+^)@", AddressLine()))
        # French address line 5
        self.assertEqual(normalize("Lieu-dit du domaine Vert", AddressLine()), "LIEU DIT DOM VERT")

    def test_address_line_forms(self):
        self.assertEqual(normalize("12 rond-point du Général de Gaulle", AddressLine()), "12 RPT GAL GAULLE")
        self.assertEqual(normalize("Ctre Cial Leclerc", AddressLine()), "CCAL LECLERC")
        self.assertEqual(normalize("Centre Commercial Grand Var", AddressLine()), "CCAL GD VAR")
        self.assertEqual(normalize("Rue du Centre", AddressLine()), "RUE CENTRE")
        self.assertEqual(normalize("Esplanade du Maréchal Foch", AddressLine()), "ESP MAL FOCH")
        self.assertEqual(normalize("3 boul. du Docteur Roux", AddressLine()), "3 BD DR ROUX")
        self.assertEqual(normalize("Paris Cx 09", AddressLine()), "PARIS CDX 09")
        self.assertEqual(normalize("1869 Chem. de Charlemagne", AddressLine()), "1869 CH CHARLEMAGNE")
        self.assertEqual(normalize("12 Fg Saint-Antoine", AddressLine()), "12 FBG ST ANTOINE")
        self.assertEqual(normalize("Z.I. des Paluds", AddressLine()), "ZI PALUDS")
        self.assertEqual(normalize("Zone Industrielle des Paluds", AddressLine()), "ZI PALUDS")
        self.assertEqual(normalize("ZA du Moulin", AddressLine()), "ZA MOULIN")
        self.assertEqual(normalize("Zone d'Aménagement Concerté de la Plaine", AddressLine()), "ZAC PLAINE")
        self.assertEqual(normalize("Promenade des Anglais", AddressLine()), "PROM ANGLAIS")
        self.assertEqual(normalize("4 Chaussée Jules César", AddressLine()), "4 CHS JULES CESAR")
        self.assertEqual(normalize("67 Cr Gambetta", AddressLine()), "67 CRS GAMBETTA")
        self.assertEqual(normalize("24 Av. du Gén de Gaulle", AddressLine()), "24 AV GAL GAULLE")
        self.assertEqual(normalize("26 b Av. du Commandant Lisiack", AddressLine()), "26 B AV CDT LISIACK")
        self.assertEqual(normalize("15 Parv. de la Défense", AddressLine()), "15 PRV DEFENSE")
        self.assertEqual(normalize("2 A Montée de Saint-Menet", AddressLine()), "2 A MTE ST MENET")
        self.assertEqual(normalize("3 Grand-Rue", AddressLine()), "3 GDE RUE")


class TestAddressLine6(TestCase):
    def test_french_address_line_6(self):
        self.assertEqual(normalize("$.75009        Paris", AddressLine6()), "75009 75 PARIS")
        self.assertEqual(normalize("75948 Paris Cedex 19", AddressLine6()), "75948 75 PARIS CDX 19")
        # If no DepartmentFrance should be inserted
        self.assertEqual(normalize("75948 Paris Cedex 19", AddressLine6(False)), "75948 PARIS CDX 19")
        # If a DepartmentFrance is already present
        self.assertEqual(normalize("75948 75 Paris Cedex 19", AddressLine6()), "75948 75 PARIS CDX 19")
        self.assertEqual(normalize("75948 75 Paris Cedex 19", AddressLine6(False)), "75948 PARIS CDX 19")


class TestAny(TestCase):
    def test_normalize_safely(self):
        self.assertEqual(normalize("Any string to normalize().", Any), "ANY STRING TO NORMALIZE")


class TestCity(TestCase):
    def test_normalize_safely(self):
        self.assertEqual(normalize("Jouy-en-Josas", City), "JOUY EN JOSAS")
        self.assertEqual(normalize("Paris      Cedex", City), "PARIS")
        self.assertEqual(normalize("CDX y", City), "Y")
        self.assertEqual(normalize("Paris Cedex  20", City), "PARIS")


class TestCodePostalFrance(TestCase):
    def test_normalize_safely(self):
        self.assertEqual(normalize("12345 ", CodePostalFrance), "12345")
        self.assertEqual(normalize("2A165", CodePostalFrance), "20165")
        self.assertEqual(normalize("75009 PARIS", CodePostalFrance), "75009")

    def test_reject_any_invalid_code_postal(self):
        self.assertIsNone(normalize("aghfkhgk", CodePostalFrance))
        self.assertIsNone(normalize("75009PARIS", CodePostalFrance))


class TestDateOfBirth(TestCase):
    def test_parse_a_date_correctly(self):
        self.assertEqual(normalize("1564/04/23", DateOfBirth("yyyy/MM/dd")), "23/04/1564")
        self.assertEqual(normalize("95/04/23", DateOfBirth("yy/MM/dd")), "23/04/1995")
        self.assertEqual(normalize("1472720661", DateOfBirth(Timestamp)), "01/09/2016")
        self.assertEqual(normalize("1472720661276", DateOfBirth(Milliseconds)), "01/09/2016")
        self.assertEqual(normalize("10 MAY 1970", DateOfBirth("DD MMM YYYY", ISO_DATE)), "19700510")
        # Hours, minutes and seconds are not supported...
        self.assertIsNone(normalize("24/04/2010 12:00:00", DateOfBirth("dd/MM/yyyy hh:mm:ss")))
        # ... avoid passing them in the format string to make it work
        self.assertEqual(normalize("24/04/2010 12:00:00", DateOfBirth("dd/MM/yyyy")), "24/04/2010")

    def test_reject_any_invalid_date(self):
        self.assertIsNone(normalize("1969", DateOfBirth(FRENCH_DATE)))
        self.assertIsNone(normalize("not-a-date", DateOfBirth()))
        self.assertIsNone(normalize("not-a-timestamp", DateOfBirth(Timestamp)))


class TestDepartementFrance(TestCase):
    def test_extract_the_appropriate_departement_number(self):
        self.assertEqual(normalize("20167", DepartementFrance), "2A")
        self.assertEqual(normalize("  75009 ", DepartementFrance), "75")


class TestEmail(TestCase):
    def test_normalize_safely(self):
        self.assertEqual(normalize(" cdever@EDGEWHERE.fr", Email), "cdever@edgewhere.fr")

    def test_reject_any_invalid_email(self):
        self.assertIsNone(normalize("pretty-long string that's not an email@at_all.com", Email))
        self.assertIsNone(normalize("gregoire.albizzati@edge@where.fr", Email))
        self.assertIsNone(normalize("t@t.t", Email))

    def test_not_change_a_valid_email(self):
        self.assertEqual(normalize("cdever@edgewhere.fr", Email), "cdever@edgewhere.fr")


class TestFirstName(TestCase):
    def test_work_as_expected(self):
        self.assertEqual(normalize("Cyril", FirstName), "CYRIL")
        self.assertEqual(normalize("J Louis", FirstName), "JEAN LOUIS")
        self.assertEqual(normalize("Unknown", FirstName), "UNKNOWN")
        self.assertIsNone(normalize("#@~*%", FirstName))
        self.assertIsNone(normalize("", FirstName))


class TestMobile(TestCase):
    def test_normalize_safely(self):
        self.assertEqual(normalize("0623456789", Mobile), "+33 (0) 623 456 789")
        self.assertEqual(normalize("07-23-45-67-89", Mobile), "+33 (0) 723 456 789")

    def test_reject_landline_phone_numbers(self):
        self.assertIsNone(normalize("01.23.45.67.89", Mobile))
        # All zero is not a valid number
        self.assertIsNone(normalize("06 00 00 00 00", Mobile))


class TestPhoneNumber(TestCase):
    def test_normalize_safely(self):
        self.assertEqual(normalize("0123456789", PhoneNumber), "+33 (0) 123 456 789")
        self.assertEqual(normalize("01-23-45-67-89", PhoneNumber), "+33 (0) 123 456 789")
        self.assertEqual(normalize("0033 0 1 23 45 67 89", PhoneNumber), "+33 (0) 123 456 789")
        # Mobile phones are phone numbers by definition
        self.assertEqual(normalize("06.23.45.67.89", PhoneNumber), "+33 (0) 623 456 789")

    def test_reject_invalid_phone_numbers(self):
        self.assertIsNone(normalize("01-23-45-67-8-10", PhoneNumber))
        self.assertIsNone(normalize("not-even-close-to-a-phone-number", PhoneNumber))
        # All zero is not a valid number
        self.assertIsNone(normalize("01 00 00 00 00", PhoneNumber))


class TestStreetNumber(TestCase):
    def test_normalize_safely(self):
        self.assertEqual(normalize("8bis", StreetNumber), "8B")
        self.assertEqual(normalize("11SEXIES", StreetNumber), "11S")
        self.assertEqual(normalize("221 bis", StreetNumber), "221B")
        self.assertEqual(normalize("1 bis C", StreetNumber), "1B")
        self.assertEqual(normalize("7ter rue Henner", StreetNumber), "7T")


class TestTitle(TestCase):
    def test_return_the_appropriate_codes(self):
        self.assertEqual(normalize("Mademoiselle", Title), "2")
        self.assertEqual(normalize("Docteur", Title), "0")
        self.assertIsNone(normalize(" ", Title))
        self.assertEqual(normalize("1", Title), "1")
        self.assertEqual(normalize("Monsieur et Madame", Title), "0")
