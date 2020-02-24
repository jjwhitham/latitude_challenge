import json


class EncodingProperties:
    """ A class for holding the encoding properties provided in 'spec.json' and
        raising exceptions for invalid specs.
        Input & output filenames and the desired output newline character are
        also stored.
    """

    def __init__(
        self,
        spec_filename,
        fixed_width_filename,
        delimited_filename,
        delimited_newline=None,
    ):

        self.spec_filename = spec_filename
        self.fixed_width_filename = fixed_width_filename
        self.delimited_filename = delimited_filename
        self.delimited_newline = delimited_newline
        self.column_names = []
        self.offsets = []
        self.fixed_width_encoding = ""
        self.delimited_encoding = ""
        self.include_header = False

        # Load spec file
        with open(spec_filename, "r") as spec_file:
            spec = json.load(spec_file)

        # Raise exception for illegal delimited_newline character
        if delimited_newline not in {None, "", "\n", "\r\n", "\r"}:
            raise ValueError(f"Illegal newline value: {delimited_newline}")

        # Set column names and offsets and assert their lengths are equal
        self.column_names = spec["ColumnNames"]
        self.offsets = list(map(int, spec["Offsets"]))
        if len(self.column_names) != len(self.offsets):
            raise ValueError("The number of column names and offsets do not match")

        # Check whether header should be written
        if spec["IncludeHeader"] == "True":
            self.include_header = True
        else:
            self.include_header = False

        # Reject specs with unrecognised fixed width encoding
        fixed_width_encoding = spec["FixedWidthEncoding"]
        if fixed_width_encoding != "windows-1252":
            raise ValueError(
                f"{fixed_width_encoding} is either not a valid encoding, or it has not been implemented."
            )
        else:
            self.fixed_width_encoding = "cp1252"

        # Reject specs with unrecognised delimited encoding
        delimited_encoding = spec["DelimitedEncoding"]
        if delimited_encoding != "utf-8":
            raise ValueError(
                f"{delimited_encoding} is either not a valid encoding or it has not been implemented."
            )
        else:
            self.delimited_encoding = "UTF-8"
