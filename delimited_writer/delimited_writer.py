"""
Data Engineering Coding Challenge - Latitude Finance
"""

import csv
import os


class DelimitedFileWriter:
    """
    Provides an interface for parsing fixed width text files and writing 
    the generated data to delimited text files (CSV).

    An encoding_props object of the EncodingProperties class is to be 
    provided upon initialisation which contains the encoding types, 
    column widths and header provided by the specification file 'spec.json'.

    Fixed width files are parsed and their newline characters are removed,
    regardless of whether they are '\r', '\n' or '\r\n'.
    
    When self.encoding_props.delimited_newline is None, or "",
    the newline character written to the delimited file will be the environment's
    default, i.e. 'os.linesep'.
    Otherwise if delimited_newline is '\r', '\n' or '\r\n', this will the character
    written.

    The following Python documentation discusses how encoding and newlines are applicable
    to the built-in function 'open()' and 'csv.writer()' used in this class:
    https://docs.python.org/3/library/functions.html#open
    https://docs.python.org/3/library/functions.html#open-newline-parameter
    https://docs.python.org/3/glossary.html#term-universal-newlines
    https://docs.python.org/3/library/os.html#os.linesep
    https://docs.python.org/3/library/csv.html#module-csv
    """

    def __init__(self, encoding_props):
        self.encoding_props = encoding_props

    def parse_fixed_width_file(self):
        """ Parses fixed width file.
            newline takes default value of None (Python Universal Newlines)
            as to ensure that any occurences of '\n', '\r' & '\r\n' are converted 
            to '\n' and then removed. This ensures independence of environment.
        """
        fixed_width_filename = self.encoding_props.fixed_width_filename
        fixed_width_encoding = self.encoding_props.fixed_width_encoding
        offsets = self.encoding_props.offsets
        delimited_data = []

        with open(
            fixed_width_filename, "r", encoding=fixed_width_encoding, newline=None
        ) as f:
            for line in f:
                line = line.replace("\n", "")
                if len(line) != sum(offsets):
                    raise ValueError("One or more fields are of incorrect length")
                # pull out each field
                line_data = [
                    line[sum(offsets[0:i]) : sum(offsets[0:i]) + offset].replace(
                        " ", ""
                    )
                    for i, offset in enumerate(offsets)
                ]
                delimited_data.append(line_data)
        return delimited_data

    def generate_delimited_file(self, delimited_data):
        """ Write the generated delimited data to file. 
            Built-in function, 'open()', is called in text mode, ensuring that 
            data is writted with encoding=delimited_encoding. With newline="", 
            it is ensured that 'open()' will not interfere with how csv.writer
            writes newline characters.

            See documentation for details:
            "Footnotes"
            https://docs.python.org/3/library/csv.html#id3
        """
        delimited_filename = self.encoding_props.delimited_filename
        delimited_encoding = self.encoding_props.delimited_encoding
        delimited_newline = self.encoding_props.delimited_newline
        include_header = self.encoding_props.include_header

        with open(
            delimited_filename, "w", encoding=delimited_encoding, newline=""
        ) as f:
            # Ensure that newline behaviour is as described in class docstrings
            if delimited_newline in {None, ""}:
                delimited_newline = os.linesep
            elif delimited_newline == "\n":
                pass
            elif delimited_newline == "\r":
                pass
            elif delimited_newline == "\r\n":
                pass

            writer = csv.writer(f, delimiter=",", lineterminator=delimited_newline)
            # Write the header out, if required
            if include_header is True:
                header = self.encoding_props.column_names
                writer.writerow(header)
            # Write out data
            for line in delimited_data:
                writer.writerow(line)
