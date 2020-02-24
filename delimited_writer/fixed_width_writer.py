import random
import os

# For generating cp1252 characters
from encodings.cp1252 import decoding_table


class MockFixedWidthFileWriter:
    """ A helper class to generate mock fixed width data for
        testing delimited_writer.py
    """

    def __init__(self, encoding_props, fixed_width_newline):
        self.encoding_props = encoding_props
        self.fixed_width_newline = fixed_width_newline

    def generate_fixed_width_data(self):
        """ Using the decoding table for cp1252, picks a random character for each column.
            Fills the column with a random multiple of this character, between 1 and the
            column length, padding to the right with spaces.
        """
        data = []
        # Generate 10 lines of data
        num_lines = 10
        for line in range(num_lines):
            line_data = []
            offsets = self.encoding_props.offsets
            for offset in offsets:
                repeats = random.randint(1, offset)
                column_data = ""
                # Choose a random char from decoding table, skipping the
                # first 33 chars, as they are hardware control chars/non-visible
                rand_char = random.randint(33, 255)
                # Replace control char (127), undefined chars ('\ufffe')
                # & no-break space (160) with "!"
                if rand_char in [127, 129, 141, 143, 144, 157, 160]:
                    rand_char = 33
                column_data += decoding_table[rand_char] * repeats
                line_data.append(column_data.ljust(offset))
            data.append(line_data)
        return data

    def write_fixed_width_file(self, fixed_width_data):
        """ Writes fixed width file with specified newline=fixed_width_newline.
            f.write("\n") to achieve this in a platform-independent way,
            as per Python docs:
            https://docs.python.org/3/library/os.html#os.linesep
        """
        fixed_width_filename = self.encoding_props.fixed_width_filename
        fixed_width_newline = self.fixed_width_newline
        fixed_width_encoding = self.encoding_props.fixed_width_encoding

        with open(
            fixed_width_filename,
            "w",
            encoding=fixed_width_encoding,
            newline=fixed_width_newline,
        ) as f:
            for line in fixed_width_data:
                for field in line:
                    f.write(field)
                f.write("\n")
