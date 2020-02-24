from delimited_writer.delimited_writer import DelimitedFileWriter
from delimited_writer.fixed_width_writer import MockFixedWidthFileWriter
from delimited_writer.encoding_properties import EncodingProperties

import unittest
import os


class CorrectEncodingDecoding(unittest.TestCase):
    """ Tests that data is correctly encoded and decoded between reading
        the fixed width file and generating the delimited data.
    """

    def setUp(self):
        spec_filename = "spec.json"
        fixed_width_filename = "fixed_width_cp1252.txt"
        delimited_filename = "delimited_utf8.txt"

        # Set encoding properties
        self.encoding_props = EncodingProperties(
            spec_filename,
            fixed_width_filename,
            delimited_filename,
            delimited_newline=None,
        )

        # Generate mock fixed width data and file
        self.fixed_width = MockFixedWidthFileWriter(
            self.encoding_props, fixed_width_newline=None
        )
        self.fixed_width_data = self.fixed_width.generate_fixed_width_data()
        self.fixed_width.write_fixed_width_file(self.fixed_width_data)

        # Generate delimited data and file
        self.delimited = DelimitedFileWriter(self.encoding_props)
        self.delimited_data = self.delimited.parse_fixed_width_file()
        self.delimited.generate_delimited_file(self.delimited_data)

    def test_correct_encoding_decoding(self):
        """ Create mock fixed width data, write data to file,
            parse this file and assert the data matches after
            encoding/decoding
        """
        number_of_lines = len(self.fixed_width_data)
        number_of_columns = len(self.fixed_width_data[0])
        for i in range(number_of_lines):
            for j in range(number_of_columns):
                fixed_width_item = self.fixed_width_data[i][j].replace(" ", "")
                delimited_item = self.delimited_data[i][j]
                self.assertEqual(fixed_width_item, delimited_item)


class ColumnLengthsMatchSpec(unittest.TestCase):
    """ Tests whether data read from a fixed width file matches the given
        spec.
    """

    def setUp(self):
        """ Create invalid column length in fixed width file using 
            bad_spec.json which has the first column's offset changed from 5 to 10.
        """
        spec_filename = "spec.json"
        bad_spec_filename = "bad_spec.json"
        fixed_width_filename = "fixed_width_cp1252.txt"
        delimited_filename = "delimited_utf8.txt"

        # Set encoding properties with good spec
        self.encoding_props = EncodingProperties(
            spec_filename,
            fixed_width_filename,
            delimited_filename,
            delimited_newline=None,
        )

        # Set encoding properties with bad spec
        self.bad_encoding_props = EncodingProperties(
            bad_spec_filename,
            fixed_width_filename,
            delimited_filename,
            delimited_newline=None,
        )

        # Generate mock fixed width data and file with bad spec
        self.fixed_width = MockFixedWidthFileWriter(
            self.bad_encoding_props, fixed_width_newline=None
        )
        self.fixed_width_data = self.fixed_width.generate_fixed_width_data()
        self.fixed_width.write_fixed_width_file(self.fixed_width_data)

    def test_invalid_sum_of_columns_raises_exception(self):
        """ Ensure that exception is raised from delimited_writer.py
            when a row of fixed length data does not sum to the sum of 
            the offset values from spec.json
        """

        # Generate delimited data and file using good spec
        self.delimited = DelimitedFileWriter(self.encoding_props)
        with self.assertRaises(Exception):
            self.delimited_data = self.delimited.parse_fixed_width_file()


class TestNewLineSeparators(unittest.TestCase):
    """ These tests ensure that the desired newline characters are correctly written to file.
        This is important as newlines vary between environments ('\n' or '\r\n', possibly '\r').

        Newlines must be handled carefully, for example:
        Replacing the '\n' in '\r\n' with '\r\n', yielding '\r\r\n', is highly undesirble.

        Mock fixed width data is written to file with fixed_width_newline character.
        This file is parsed and a delimited file created with the desired delimited_newline character.

        Both of these files are then read with newline="" such that no newline replacements occur.
        Then each newline character read is asserted equal to the desired newline character written.

        N.B. The following table summarises how the 'newline' kwarg in the built-in 'open()' function
        handles line separators when reading and writing files.

        As per the Python documentation:
        https://docs.python.org/3/library/functions.html#open-newline-parameter
        
        ----------------------------------------------------------------------------------    
        __________|__Newline:______________Replacement:___________________________________
        Read 'r': |  None (default)        '\r', '\n', '\r\n' --> replaced with '\n', 
                  |                         & universal newlines enabled.
                  |
                  |       ""                No replacements. Universal newline enabled.
                  |
                  |'\r' or '\n' or '\r\n'   No replacements. Line split on chosen separator.
                  |
       Write 'w': |  None (default)         '\n' --> replaced with os.linesep
                  |
                  |   "" or '\n'            No replacements
                  |
                  | '\r' or '\r\n'          '\n'--> replaced with '\r' or '\r\n'  
    """

    def setUp(self):
        self.fixed_width_filename = "fixed_width_cp1252.txt"
        self.delimited_filename = "delimited_utf8.txt"
        self.spec_filename = "spec.json"

    def test_newlines(self):
        """ Try all combinations of allowable newlines. Testing both the mock fixed width
            and delimited files.
        """
        newlines = [None, "", "\r\n", "\r", "\n"]
        for fixed_width_newline in newlines:
            for delimited_newline in newlines:
                self.helper_test_newlines(fixed_width_newline, delimited_newline)

    def test_illegal_delimited_newline(self):
        """ Ensure that a newline character not in {None, "", "\r\n", "\r" ,"\n"}
            raises an exception.
        """
        fixed_width_newline = None
        delimited_newline = "\t"
        with self.assertRaises(Exception):
            self.helper_test_newlines(fixed_width_newline, delimited_newline)

    def helper_test_newlines(self, fixed_width_newline, delimited_newline):
        """ Write fixed width file with fixed_width_newline newline character.
            Read fixed width file and assert that the newline character is as
            intended.

            Write delimited file with delimited_newline newline character.
            Read delimited file and assert that the newline character is as
            intended.
        """

        # Set encoding properties
        encoding_props = EncodingProperties(
            self.spec_filename,
            self.fixed_width_filename,
            self.delimited_filename,
            delimited_newline,
        )

        # Generate mock fixed width data and file
        fixed_width = MockFixedWidthFileWriter(encoding_props, fixed_width_newline)
        fixed_width_data = fixed_width.generate_fixed_width_data()
        fixed_width.write_fixed_width_file(fixed_width_data)

        # Generate delimited data and file
        delimited = DelimitedFileWriter(encoding_props)
        delimited_data = delimited.parse_fixed_width_file()
        delimited.generate_delimited_file(delimited_data)

        # newline is "", i.e. do not replace newline character, read as is
        with open(self.fixed_width_filename, "r", encoding="cp1252", newline="") as f:
            for line in f:
                if fixed_width_newline == None:
                    fixed_width_newline = os.linesep
                elif fixed_width_newline in {"", "\n"}:
                    fixed_width_newline == "\n"
                linesep_length = len(fixed_width_newline)

                linesep_from_file = repr(line[len(line) - linesep_length :])
                self.assertEqual(linesep_from_file, repr(fixed_width_newline))

        # newline is "", i.e. do not replace newline character, read as is
        with open(self.delimited_filename, "r", encoding="utf-8", newline="") as f:
            for line in f:
                if delimited_newline in {"", None}:
                    delimited_newline = os.linesep
                linesep_length = len(delimited_newline)

                linesep_from_file = repr(line[len(line) - linesep_length :])
                self.assertEqual(linesep_from_file, repr(delimited_newline))


class WrongFixedWidthFileEncoding(unittest.TestCase):
    """ This test asserts that an exception is raised when parsing a
        fixed width file that is not of the specified encoding type.

        Tested by writing a delimited UTF-8 file and feeding this into
        the delimited writer as input
    """

    def setUp(self):
        spec_filename = "spec.json"
        fixed_width_filename = "fixed_width_cp1252.txt"
        delimited_filename = "delimited_utf8.txt"

        # Set encoding properties
        self.encoding_props = EncodingProperties(
            spec_filename,
            fixed_width_filename,
            delimited_filename,
            delimited_newline=None,
        )

        # Generate mock fixed width data and file
        self.fixed_width = MockFixedWidthFileWriter(
            self.encoding_props, fixed_width_newline=None
        )
        self.fixed_width_data = self.fixed_width.generate_fixed_width_data()
        self.fixed_width.write_fixed_width_file(self.fixed_width_data)

        # Generate delimited data and file
        self.delimited = DelimitedFileWriter(self.encoding_props)
        self.delimited_data = self.delimited.parse_fixed_width_file()
        self.delimited.generate_delimited_file(self.delimited_data)

    def test_wrong_fixed_encoding_raises_exception(self):
        """ Use delimited_utf8.txt as input to delimited writer.
            Assert exception is raised.
        """
        with self.assertRaises(Exception):
            spec_filename = "spec.json"
            fixed_width_filename = "delimited_utf8.txt"
            delimited_filename = "delimited_utf8.txt"

            self.encoding_props = EncodingProperties(
                spec_filename,
                fixed_width_filename,
                delimited_filename,
                delimited_newline=None,
            )
            self.delimited = DelimitedFileWriter(self.encoding_props)
            self.delimited_data = self.delimited.parse_fixed_width_file()


if __name__ == "__main__":

    unittest.main()
