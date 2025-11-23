from dataclasses import dataclass
from typing import List


class Error:
    def __init__(self, name: str, regex: str, entries: List[str] = []) -> None:
        self.name: str = name
        self.regex: str = regex
        self.entries: List[str] = entries

    def __str__(self) -> str:
        return f'Error("{self.name}", "{self.regex}")'


ERRORS_BY_CATEGORY = {
    "Lexical and Token Errors": [
        Error("x expected, not y.", ".* expected, not .*"),
        Error("x expected after y", ".* expected after .*"),
        Error("Unable to interpret x.", 'Unable to interpret ".*"\\.'),
        Error("Comma without preceding colon", "Comma without preceding colon .*"),
        Error("The statement x is invalid. Check the spelling.", "The statement .* is invalid. Check the spelling."),
        Error("The variable x must be escaped using @.", 'The variable .* must be escaped using "@"\\.'),
        Error("x is not allowed here. y is expected.", ".* is not allowed here. .* is expected\\."),
        Error(
            "The statement before x was not closed (period missing).",
            "The statement before .* was not closed \\(period missing\\)\\.",
        ),
        Error(
            "There must be a space or equivalent character after x.",
            "There must be a space or equivalent character .* after .*\\.",
        ),
        Error("Unmasked symbol in string template", "Unmasked symbol '\\|' in string template\\."),
        Error("Names may consist only of x characters.", "Names may consist only of the characters .*"),
        Error("Unexpected operator", 'Unexpected operator ".*"\\.'),
        Error("Numeric literals cannot be used as field names.", "Numeric literals cannot be used as field names\\."),
        Error("Relational operator x is not supported.", "Relational operator .* is not supported."),
        Error("Multiline literal are not allowed.", "Literals across more than one line are not allowed."),
        Error("Invalid regular expression", "Regular expression '.*' is invalid in character position \\d+\\."),
        Error("SQLSCRIPT:", "SQLSCRIPT:.*"),
        Error(
            "INDEX not allowed with generic INSERT INTO TABLE",
            'INDEX cannot be specified with a generic INSERT statement \\(addition "INTO TABLE"\\)\\.',
        ),
    ],
    "Structural and Formatting Errors": [
        Error("The statement x is unexpected.", "The statement .* is unexpected"),
        Error("x is missing between y and z.", '".*" is missing between ".*" and ".*".'),
        Error("The statement ended unexpectedly.", "The statement .* ended unexpectedly."),
        Error("Incorrect nesting:", "Incorrect nesting.*"),
        Error(
            "Offset and/or length specifications without values like x are not allowed.",
            "Offsets? (and|or) lengths? .*",
        ),
        Error(
            "The statement x is not expected. A correct similar statement is y.",
            "The statement .* is not expected. A correct similar statement is .*\\.",
        ),
        Error("x is invalid here (due to grammar).", ".* is invalid here \\(due to grammar\\)\\."),
        Error("Incomplete arithmetic expression", "Incomplete arithmetic expression.*"),
        Error(
            "The elements in the x list must be separated using commas.",
            "The elements in the .* list must be separated using commas.",
        ),
        Error("Three-figure number required", 'No three-figure number is specified in ".*"\\.'),
        Error("The source code of this class is incomplete", "The source code of this class is incomplete"),
        Error(
            "Expression limiter not followed by space",
            "Expression limiter '\\{' in string template not followed by space\\.",
        ),
        Error("Invalid format of numbered statement", 'Format of ".*" is incorrect\\.'),
        Error(
            "Statement '0' must be followed by additions", "The statement '0' must be followed by other additions\\."
        ),
        Error("Missing parenthesis after method name", 'Missing "\\(" after the method name\\.'),
        Error("ENDMETHOD statement is missing.", 'The statement "ENDMETHOD" is missing\\.'),
        Error("FOR expression not specified.", '"FOR ... " is not specified\\.'),
        Error(
            "The format of specified field x is not supported.",
            "The format of specified field .* is not supported\\..*",
        ),
        Error("Component does not exist", 'No component exists with the name ".*"\\.'),
        Error(
            'There is no "PUBLIC ...", "PROTECTED..." or "PRIVATE SECTION" statement.',
            'There is no "PUBLIC ...", "PROTECTED..." or "PRIVATE SECTION" statement\\.',
        ),
        Error(
            "No method can be specified in the current position.",
            "No method can be specified in the current position\\.",
        ),
        Error(
            "The data object x does not have a component called y.",
            "The data object .* does not have a component called .*\\.",
        ),
        Error("Cannot define global class inside another class", "You may not define the global class .* in class .*"),
        Error(
            "The key is not specified in full. Types specified generically are completed only in standard tables.",
            "The key is not specified in full. Types specified generically are completed only in standard tables\\.",
        ),
        Error(
            "x does not have the structure of a selection table.",
            ".* does not have the structure of a selection table\\.",
        ),
        Error("Invalid syntax for a table row selection.", "Invalid syntax for a table row selection\\."),
        Error(
            "Substrings cannot be accessed in internal tables, deep structures, or references.",
            "Substrings cannot be accessed in internal tables, deep structures, or references\\.",
        ),
        Error("Structure or internal table expected", '".*" is not a structure or an internal table\\.'),
        Error(
            "SORT not supported for SORTED tables",
            '".*" is a table of the type SORTED\\. The SORT command cannot be used with this type of table\\.',
        ),
        Error("Table x does not have a key y.", 'Table ".*" does not have a key ".*"\\.'),
        Error(
            "Table cannot be modified within a LOOP across itself.",
            'The table ".*" cannot be deleted or overwritten within a LOOP across itself\\.',
        ),
        Error(
            "Header line required for internal table.",
            'The internal table ".*" does not have a header line; work area must be specified explicitly \\("FROM wa"\\)\\.',
        ),
        Error(
            "Table must be STANDARD and without secondary keys.",
            'In this statement, the internal table ".*" must have the type "STANDARD TABLE" and cannot have any secondary keys\\.',
        ),
        Error(
            "x is not a permitted operator in this position of the calculation expression.",
            ".* is not a permitted operator in this position of the calculation expression\\.",
        ),
        Error("Error in logical expression.", "Error in logical expression.*"),
        Error("Invalid line break in string template.", "Invalid line break in string template\\."),
        Error(
            "Text literal is too long.",
            "The text literal .* is longer than 255 characters. Check whether it ends correctly\\.",
        ),
        Error("Format directive unknown or invalid", 'Format directive ".*" (cannot be applied|unknown)\\.'),
        Error("Unknown format specifier", 'Format ".*" unknown\\.'),
        Error(
            "MATCH LINE, MATCH OFFSET, and MATCH LENGTH cannot be used with RESULTS.",
            "The additions MATCH LINE, MATCH OFFSET, and MATCH LENGTH cannot be used with RESULTS\\.",
        ),
        Error(
            "ALL OCCURRENCES requires at least one return value.",
            "The addition ALL OCCURRENCES requires at least one return value to be queried\\.",
        ),
        Error(
            "ALPHA format directive cannot be applied to embedded expression.",
            'Format directive "ALPHA" cannot be applied to the embedded expression\\.',
        ),
        Error(
            "The INTO/APPENDING clause must be at the end of the SELECT.",
            "The INTO/APPENDING clause must be at the end of the SELECT.*",
        ),
        Error(
            "Missing FROM in DML statement", 'The addition "FROM" for DELETE, INSERT, MODIFY, or UPDATE is missing\\.'
        ),
        Error("Missing INTO clause in SELECT", "Field list without INTO clause is not allowed\\."),
        Error(
            "Missing INTO/ASSIGNING in SELECT",
            'Specify one of the additions "INTO wa", "ASSIGNING", "REFERENCE INTO", or "TRANSPORTING NO FIELDS"\\.',
        ),
        Error(
            "Missing ORDER BY before OFFSET",
            "If an OFFSET addition exists, an ORDER BY clause must also be specified.*",
        ),
        Error("INTO clause required for target area.", "A target area must be specified using an INTO clause\\."),
        Error("Work area has fewer fields than selected.", 'The work area ".*" has fewer fields than selected\\.'),
        Error(
            "x is allowed only within loops (DO, WHILE, LOOP, SELECT).",
            ".* is allowed only within loops \\(DO, WHILE, LOOP, SELECT\\)\\.",
        ),
        Error(
            "Missing INTO/ASSIGNING in LOOP AT",
            'In "LOOP AT .*", one of the additions .* is required in the .* context\\.',
        ),
        Error("Missing open IF statement", 'No open "IF" statement exists\\.'),
        Error("WRITE TO does not support formatting", "WRITE TO cannot specify any positions, lengths, or formats.*"),
    ],
    "Type and Conversion Errors": [
        Error("Negative lengths are not allowed", "Lengths < 0 cannot be specified\\."),
        Error("Invalid operand for IN.", 'Invalid operand for "IN"\\.'),
        Error(
            "x must be a character-like data object.",
            "must be a character-like data object \\(data type C, N, D, T, or STRING\\)\\.",
        ),
        Error(
            "Field type .* does not permit substrings to be accessed.",
            "Field type .* does not permit substrings to be accessed\\.",
        ),
        Error("The type x is not a structure.", "The type .* is not a structure\\."),
        Error(
            "The type of x cannot be converted to the type of y.",
            "The type of .* cannot be converted to the type of .*",
        ),
        Error("x and the row type of y are incompatible.", ".* and the row type of .* are incompatible\\."),
        Error(
            "x is a generic type. Use this type only for typing field symbols and formal parameters.",
            ".* is a generic type\\. Use this type only for typing field symbols and formal parameters\\.",
        ),
        Error(
            "x can only be specified for types C, N, X, or P.", ".* can only be specified for types C, N, X, or P\\."
        ),
        Error(
            "A value of the generic type x cannot be constructed.",
            "A value of the generic type .* cannot be constructed\\.",
        ),
        Error(
            "No type can be derived for operator", 'No type can be derived from the context for the operator ".*"\\.'
        ),
        Error(
            "Incompatible data type",
            'The data type of the component ".*" of ".*" is not compatible with the data type of ".*".*',
        ),
        Error(
            "Unicode conversion issue",
            'Rows of ".*" and ".*" cannot be converted to each other in a Unicode program\\.',
        ),
        Error("Invalid conversion to character-like value", '".*" cannot be converted to a character-like value\\.'),
        Error(
            "Invalid result type for method",
            "The result type of the functional method cannot be converted into the type of .*",
        ),
        Error("Invalid length for type P", 'For type "P", a length from 1 to 16 can be specified\\.'),
        Error("Incompatible assignment", "The data type of .* is not compatible with the data type of .*\\."),
        Error(
            "SY-FDPOS must be compatible with MATCH_RESULT or MATCH_RESULT_TAB.",
            'The type of ".*" must be compatible with the type\\(s\\) of ".*"\\.',
        ),
        Error(
            "Operands cannot be converted to each other in a Unicode program.",
            '".*" and ".*" cannot be converted to each other in a Unicode program\\.',
        ),
        Error(
            "Too many decimal places specified.",
            'Number of decimal places specified in ".*" is too great: Maximum allowed is \\d+\\.',
        ),
        Error(
            "Generic types not allowed in structures.", "Generic type definitions cannot be used within structures\\."
        ),
        Error("Not an internal table type.", '".*" is not the type of an internal table\\.'),
        Error(
            "DECIMALS must be specified with P types.",
            "DECIMALS must be specified when using P types in the OO context\\.",
        ),
        Error(
            "Generic table categories not allowed for data objects.",
            'Data objects cannot be typed generically. The table categories ".*" are generic\\.',
        ),
        Error(
            "Data type N is not allowed in function LOWER.",
            'The data type ".*" is not allowed in the function "LOWER".*',
        ),
        Error("X or XSTRING required.", '".*" must have the type X or XSTRING\\.'),
        Error("Cannot convert value into a number.", '".*" cannot be converted into a number\\.'),
        Error("x is not an internal table.", '".*" is not an internal table\\.'),
        Error("x cannot be converted to the row type of y.", ".* cannot be converted to the row type of .*"),
        Error(
            "Only tables with a character-like row type (data type C, N, D, T, or STRING) are allowed with the addition x.",
            "Only tables with a character-like row type \\(data type C, N, D, T, or STRING\\) are allowed with the addition .*\\.",
        ),
        Error(
            "Explicit or implicit index operations cannot be used on tables with type x",
            "Explicit or implicit index operations cannot be used on tables with types.*\\.",
        ),
        Error("A x parameter must be fully typed.", "A .* parameter must be fully typed\\."),
        Error(
            "Returning parameters must be passed as value.",
            "RETURNING parameters must be specified to be passed as VALUE\\(\\)\\.",
        ),
        Error(
            "The generic types cannot be specified in returning parameters.",
            "The generic types .* cannot be specified in RETURNING parameters\\.",
        ),
        Error(
            "x is not type-compatible with formal parameter y.", ".* is not type-compatible with formal parameter .*\\."
        ),
        Error(
            "The formal parameter x is a y parameter, not a z parameter.",
            "The formal parameter .* is a .* parameter, not a .* parameter\\.",
        ),
        Error("Error in arithmetic expression", "Error in arithmetic expression.*"),
        Error("A Boolean expression was expected in x.", "A Boolean expression was expected in .*\\."),
        Error(
            "Arithmetic expression cannot be compared with non-numeric operand",
            'An arithmetic expression cannot be compared with the non-numeric operand ".*"\\.',
        ),
        Error("Arithmetic calculation not permitted", "Arithmetic calculation not permitted here\\."),
        Error(
            "AMDP: Only elementary or table-like IMPORTING parameters allowed with RETURNING.",
            "In AMDP methods, only elementary or table-like IMPORTING parameters are allowed in combination with RETURNING.*",
        ),
    ],
    "OOP Errors": [
        Error("Chained attribute access not allowed", "Chained access to attributes is not allowed\\."),
        Error(
            "Lengths must be specified explicitly when using types C, P, X, and N in the OO context.",
            "Lengths must be specified explicitly when using types C, P, X, and N in the OO context\\.",
        ),
        Error("Field is not a class reference", 'Field ".*" is not a reference to the class .*'),
        Error("REF TO cannot be used with generic types.", 'A generic type cannot be specified after "REF TO"\\.'),
        Error("Method is unknown or PROTECTED or PRIVATE.", 'Method ".*" is unknown or PROTECTED or PRIVATE\\.'),
        Error(
            "The method x is not declared or inherited in class y.",
            "The method .* is not declared or inherited in class .*\\.",
        ),
        Error(
            "class=>method can only be specified with static methods.",
            '"class=>method" can only be specified with static methods\\.',
        ),
        Error(
            "Instances of the abstract class x cannot be generated.",
            "Instances of the abstract class .* cannot be generated\\.",
        ),
        Error(
            "An instance of the class x cannot be created outside the class.",
            "An instance of the class .* cannot be created outside the class\\.",
        ),
        Error("Class x does not contain an interface y.", "Class .* does not contain an interface .*\\."),
        Error(
            "Only static methods can be specified using the short form (method) within a static method.",
            "Only static methods can be specified using the short form \\(method\\) within a static method\\.",
        ),
        Error(
            "Within a static method, only static attributes can be accessed without specifying further information.",
            "Within a static method, only static attributes can be accessed without specifying further information\\.",
        ),
        Error(
            "Unsupported TYPE/DECIMALS in OO",
            "The additions TYPE and DECIMALS are no longer supported in the OO context.*",
        ),
        Error(
            "READ-ONLY only allowed for public attributes",
            "The addition READ-ONLY is only allowed for the public attributes.*",
        ),
        Error("CLASS_CONSTRUCTOR must be PUBLIC", '"CLASS_CONSTRUCTOR" must always be PUBLIC\\.'),
        Error("Untyped field symbols not allowed in OO", "Untyped field symbols are not supported in the OO context.*"),
        Error(
            "Tables with headers are no longer supported in the OO context.",
            "Tables with headers are no longer supported in the OO context\\.",
        ),
        Error(
            "The addition OCCURS is no longer supported in the OO context.",
            "The addition OCCURS is no longer supported in the OO context.*",
        ),
        Error(
            "Implicit keys no longer supported in OO context.",
            "Keys can no longer be specified implicitly in the OO context.*",
        ),
        Error(
            "Constructor visibility too specific for instance creator.",
            "Visibility of the constructor cannot be more specific than the visibility of the instance creator.*",
        ),
        Error(
            "Method result must be an object or data reference.",
            'The result of the method ".*" must be an object reference or data reference\\.',
        ),
        Error("Method does not exist.", "Method .* does not exist\\."),
        Error(
            "AMDP class must implement IF_AMDP_MARKER_HDB.",
            'Database procedures managed by ABAP can only be defined in classes that implement the marker interface "IF_AMDP_MARKER_HDB"\\.',
        ),
    ],
    "Declaration Errors": [
        Error("x is not valid.", ".* is not valid."),
        Error(
            "The name is longer than the allowed 30 characters.",
            r'The name ".*" is longer than the allowed 30 characters.',
        ),
        Error(
            "The component x has been declared multiple times.", r"The component .* has been declared multiple times"
        ),
        Error("Inline declaration not allowed here", r"The inline declaration .* is not possible in this position\."),
        Error(
            "Between two identifiers, TYPE or LIKE is missing.", r'Between ".*" and ".*", "TYPE" or "LIKE" is missing\.'
        ),
        Error("type x is unknown.", r'type ".*" is unknown'),
        Error("Field x is unknown.", r'Field ".*" is unknown\.'),
        Error("x is not a constant.", r'" .*" is not a constant\.'),
        Error("The x does not have a structure.", r"The .* does not have a structure"),
        Error("x is not a field name.", r".* is not a field name\."),
        Error("x was already declared.", r".* was already declared\."),
        Error("x must be a y field.", r".* must be a .* field .*\."),
        Error(
            "x has a generic type that cannot be used for declarations.",
            r".* has a generic type that cannot be used for declarations\.",
        ),
        Error(
            "TABLE_LINE is reserved and cannot be used",
            r'"TABLE_LINE" is a reserved component name and therefore cannot be used here\.',
        ),
        Error(
            "Initial values for internal tables/references not allowed",
            r"No initial value can be specified for internal tables and references\.",
        ),
        Error(
            "Fully typed field symbol already declared",
            r'The addition TYPE or LIKE does not make any sense, since the field symbol ".*" is already fully typed\.',
        ),
        Error("Field symbol not defined", r'" .*" is not defined as a field symbol\.'),
        Error(
            "Type must be fully specified",
            r"When a type reference is used with TYPE, the type specified after TYPE must be specified in full.*",
        ),
        Error("Variable is not a reference.", r'" .*" is not a reference variable\.'),
        Error(
            "Field must be an object or data reference.",
            r'The field ".*" must be an object reference or data reference\.',
        ),
        Error(
            "Predefined object SPACE cannot be redefined.", r'The predefined data object "SPACE" cannot be redefined\.'
        ),
        Error("Class statement PUBLIC is missing.", r'The addition "PUBLIC"'),
        Error(
            'The parameter name can be omitted only if the method has only one non-optional IMPORTING parameter or one optional IMPORTING parameter identified by "PREFERRED PARAMETER".',
            r'The parameter name can be omitted only if the method has only one non-optional IMPORTING parameter or one optional IMPORTING parameter identified by "PREFERRED PARAMETER"\.',
        ),
        Error(
            "RETURNING parameter not allowed in database procedure method.",
            r'The method ".*" contains a database procedure, which means that ".*" cannot be defined as a RETURNING parameter\.',
        ),
        Error(
            "UNIQUE can only be specified with the table categories HASHED and SORTED.",
            r"UNIQUE can only be specified with the table categories HASHED and SORTED\.",
        ),
        Error("Primary key definition expected", r"A primary key of the form .* is expected\."),
        Error("The method does not have a returning parameter.", r"The method .* does not have a RETURNING parameter"),
        Error(
            "Type definition can only be specified once.", r'The addition "... TYPE type" can only be specified once\.'
        ),
        Error("The formal parameter x does not exist.", r"The formal parameter .* does not exist\."),
        Error(
            "Preferred parameter must be listed as IMPORTING",
            r"The parameter .* specified in the addition PREFERRED PARAMETER is not listed as an IMPORTING parameter\.",
        ),
        Error("Method does not have parameters", r'Method ".*" does not have any parameters\.'),
        Error(
            "No value was passed to the mandatory parameter.", r'No value was passed to the mandatory parameter ".*"\.'
        ),
        Error(
            "IS SUPPLIED only works with optional parameters.",
            r'The "IS SUPPLIED" query works only for optional parameters\.',
        ),
        Error("x cannot be modified.", r'" .*" cannot be modified\.'),
        Error(
            'The ABAP Dictionary structure or table "LT_CANDIDATE_IDS" is either not active or does not exist.',
            r"The ABAP Dictionary structure or table .* is either not active or does not exist\.",
        ),
        Error(
            "Table is not defined in the ABAP Dictionary.",
            r'" .*" is not declared as a table, projection view, or database view in ABAP Dictionary or does not exist in an active version\.',
        ),
        Error("Unknown predefined function", r'Predefined function ".*" is unknown\.'),
        Error(
            "Message class must be specified correctly",
            r'The message class must either be in parentheses after the number or specified using the addition "MESSAGE-ID".*',
        ),
        Error("Other", r".*"),
    ],
}
