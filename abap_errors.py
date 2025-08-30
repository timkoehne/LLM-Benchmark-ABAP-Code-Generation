from typing import List


class Error:
    def __init__(self, name: str, regex: str, entries: List[str] = []) -> None:
        self.name: str = name
        self.regex: str = regex
        self.entries: List[str] = entries


ERRORS_BY_CATEGORY = {
    "Syntax and Grammar Errors": [
        Error("x is not valid.", r".* is not valid."),
        Error("x expected, not y.", r".* expected, not .*"),
        Error("x expected after y", r".* expected after .*"),
        Error("Unable to interpret x.", r'Unable to interpret ".*"\.'),
        Error("The statement x is unexpected.", r"The statement .* is unexpected"),
        Error(
            "x is missing between y and z.",
            r"\".*\" is missing between \".*\" and \".*\".",
        ),
        Error(
            "The statement ended unexpectedly.", r"The statement .* ended unexpectedly."
        ),
        Error("Comma without preceding colon", r"Comma without preceding colon .*"),
        Error(
            "The statement x is invalid. Check the spelling.",
            r"The statement .* is invalid. Check the spelling.",
        ),
        Error("Incorrect nesting:", r"Incorrect nesting.*"),
        Error(
            "The name is longer than the allowed 30 characters.",
            r"The name \".*\" is longer than the allowed 30 characters.",
        ),
        Error(
            "The variable x must be escaped using @.",
            r"The variable .* must be escaped using \"@\"\.",
        ),
        Error(
            "x is not allowed here. y is expected.",
            r".* is not allowed here. .* is expected\.",
        ),
        Error(
            "Offset and/or length specifications without values like x are not allowed.",
            r"Offsets? (and|or) lengths? .*",
        ),
        Error(
            "The statement x is not expected. A correct similar statement is y.",
            r"The statement .* is not expected. A correct similar statement is .*\.",
        ),
        Error(
            "The statement before x was not closed (period missing).",
            r"The statement before .* was not closed \(period missing\)\.",
        ),
        Error(
            "x is invalid here (due to grammar).",
            r".* is invalid here \(due to grammar\)\.",
        ),
        Error(
            "Incomplete arithmetic expression", r"Incomplete arithmetic expression.*"
        ),
        Error(
            "There must be a space or equivalent character after x.",
            r"There must be a space or equivalent character .* after .*\.",
        ),
        Error(
            "The elements in the x list must be separated using commas.",
            r"The elements in the .* list must be separated using commas.",
        ),
        Error(
            "The component x has been declared multiple times.",
            r"The component .* has been declared multiple times",
        ),
        Error(
            "Unmasked symbol in string template",
            r"Unmasked symbol '\|' in string template\.",
        ),
        Error(
            "Inline declaration not allowed here",
            r"The inline declaration .* is not possible in this position\.",
        ),
        Error(
            "Chained attribute access not allowed",
            r"Chained access to attributes is not allowed\.",
        ),
        Error(
            "Three-figure number required",
            r"No three-figure number is specified in \".*\"\.",
        ),
        Error("Negative lengths are not allowed", r"Lengths < 0 cannot be specified\."),
        Error(
            "Names may consist only of x characters.",
            r"Names may consist only of the characters .*",
        ),
        Error(
            "The source code of this class is incomplete",
            r"The source code of this class is incomplete",
        ),
        Error(
            "Expression limiter not followed by space",
            r"Expression limiter '\{' in string template not followed by space\.",
        ),
        Error("Unexpected operator", r"Unexpected operator \".*\"\."),
        Error(
            "Invalid format of numbered statement", r"Format of \".*\" is incorrect\."
        ),
        Error(
            "Statement '0' must be followed by additions",
            r"The statement '0' must be followed by other additions\.",
        ),
        Error(
            "Missing parenthesis after method name",
            r"Missing \"\(\" after the method name\.",
        ),
        Error(
            "Between two identifiers, TYPE or LIKE is missing.",
            r"Between \".*\" and \".*\", \"TYPE\" or \"LIKE\" is missing\.",
        ),
        Error(
            "ENDMETHOD statement is missing.",
            r"The statement \"ENDMETHOD\" is missing\.",
        ),
        Error("FOR expression not specified.", r"\"FOR \.\.\. \" is not specified\."),
        Error("Invalid operand for IN.", r"Invalid operand for \"IN\"\."),
    ],
    "Type and Data Object Errors": [
        Error("type x is unknown.", r"type \".*\" is unknown"),
        Error("Field x is unknown.", r"Field \".*\" is unknown."),
        Error("x is not a constant.", r"\".*\" is not a constant."),
        Error("The x does not have a structure.", r"The .* does not have a structure"),
        Error(
            "x must be a character-like data object.",
            r"must be a character-like data object \(data type C, N, D, T, or STRING\)\.",
        ),
        Error(
            "Lengths must be specified explicitly when using types C, P, X, and N in the OO context.",
            r"Lengths must be specified explicitly when using types C, P, X, and N in the OO context.",
        ),
        Error(
            "Field type .* does not permit substrings to be accessed.",
            r"Field type .* does not permit substrings to be accessed\.",
        ),
        Error("The type x is not a structure.", r"The type .* is not a structure\."),
        Error(
            "The type of x cannot be converted to the type of y.",
            r"The type of .* cannot be converted to the type of .*",
        ),
        Error(
            "x and the row type of y are incompatible.",
            r".* and the row type of .* are incompatible\.",
        ),
        Error("x is not a field name.", r".* is not a field name\."),
        Error("x was already declared.", r".* was already declared\."),
        Error(
            "x is a generic type. Use this type only for typing field symbols and formal parameters.",
            r".* is a generic type\. Use this type only for typing field symbols and formal parameters\.",
        ),
        Error(
            "The format of specified field x is not supported.",
            r"The format of specified field .* is not supported\..*",
        ),
        Error(
            "x can only be specified for types C, N, X, or P.",
            r".* can only be specified for types C, N, X, or P\.",
        ),
        Error("x must be a y field.", r".* must be a .* field .*\."),
        Error(
            "x has a generic type that cannot be used for declarations.",
            r".* has a generic type that cannot be used for declarations.",
        ),
        Error(
            "A value of the generic type x cannot be constructed.",
            r"A value of the generic type .* cannot be constructed\.",
        ),
        Error(
            "Component does not exist", r"No component exists with the name \".*\"\."
        ),
        Error(
            "No type can be derived for operator",
            r"No type can be derived from the context for the operator \".*\"\.",
        ),
        Error(
            "TABLE_LINE is reserved and cannot be used",
            r"\"TABLE_LINE\" is a reserved component name and therefore cannot be used here\.",
        ),
        Error(
            "Initial values for internal tables/references not allowed",
            r"No initial value can be specified for internal tables and references\.",
        ),
        Error(
            "Incompatible data type",
            r"The data type of the component \".*\" of \".*\" is not compatible with the data type of \".*\".*",
        ),
        Error(
            "Unicode conversion issue",
            r"Rows of \".*\" and \".*\" cannot be converted to each other in a Unicode program\.",
        ),
        Error(
            "Fully typed field symbol already declared",
            r"The addition TYPE or LIKE does not make any sense, since the field symbol \".*\" is already fully typed\.",
        ),
        Error(
            "Invalid conversion to character-like value",
            r"\".*\" cannot be converted to a character-like value\.",
        ),
        Error(
            "Field symbol not defined",
            r"\".*\" is not defined as a field symbol\.",
        ),
        Error(
            "Invalid result type for method",
            r"The result type of the functional method cannot be converted into the type of .*",
        ),
        Error(
            "Invalid length for type P",
            r"For type \"P\", a length from 1 to 16 can be specified\.",
        ),
        Error(
            "Incompatible assignment",
            r"The data type of .* is not compatible with the data type of .*\.",
        ),
        Error(
            "Type must be fully specified",
            r"When a type reference is used with TYPE, the type specified after TYPE must be specified in full.*",
        ),
        Error(
            "Field is not a class reference",
            r"Field \".*\" is not a reference to the class .*",
        ),
        Error(
            "SY-FDPOS must be compatible with MATCH_RESULT or MATCH_RESULT_TAB.",
            r"The type of \".*\" must be compatible with the type\(s\) of \".*\"\.",
        ),
        Error(
            "Operands cannot be converted to each other in a Unicode program.",
            r"\".*\" and \".*\" cannot be converted to each other in a Unicode program\.",
        ),
        Error(
            "REF TO cannot be used with generic types.",
            r"A generic type cannot be specified after \"REF TO\"\.",
        ),
        Error(
            "Too many decimal places specified.",
            r"Number of decimal places specified in \".*\" is too great: Maximum allowed is \d+\.",
        ),
        Error("Variable is not a reference.", r"\".*\" is not a reference variable\."),
        Error(
            "Generic types not allowed in structures.",
            r"Generic type definitions cannot be used within structures\.",
        ),
        Error(
            "Field must be an object or data reference.",
            r"The field \".*\" must be an object reference or data reference\.",
        ),
        Error(
            "Numeric literals cannot be used as field names.",
            r"Numeric literals cannot be used as field names\.",
        ),
        Error(
            "Not an internal table type.",
            r"\".*\" is not the type of an internal table\.",
        ),
        Error(
            "DECIMALS must be specified with P types.",
            r"DECIMALS must be specified when using P types in the OO context\.",
        ),
        Error(
            "Generic table categories not allowed for data objects.",
            r"Data objects cannot be typed generically. The table categories \".*\" are generic\.",
        ),
        Error(
            "Predefined object SPACE cannot be redefined.",
            r"The predefined data object \"SPACE\" cannot be redefined\.",
        ),
        Error(
            "Data type N is not allowed in function LOWER.",
            r"The data type \".*\" is not allowed in the function \"LOWER\".*",
        ),
        Error("X or XSTRING required.", r"\".*\" must have the type X or XSTRING\."),
        Error(
            "Cannot convert value into a number.",
            r"\".*\" cannot be converted into a number\.",
        ),
    ],
    "Object-Oriented (OO) Errors": [
        Error("Class statement PUBLIC is missing.", r"The addition \"PUBLIC\""),
        Error(
            "Method is unknown or PROTECTED or PRIVATE.",
            r"Method \".*\" is unknown or PROTECTED or PRIVATE.",
        ),
        Error(
            "The method x is not declared or inherited in class y.",
            r"The method .* is not declared or inherited in class .*\.",
        ),
        Error(
            'There is no "PUBLIC ...", "PROTECTED..." or "PRIVATE SECTION" statement.',
            r"There is no \"PUBLIC ...\", \"PROTECTED...\" or \"PRIVATE SECTION\" statement\.",
        ),
        Error(
            "No method can be specified in the current position.",
            r"No method can be specified in the current position\.",
        ),
        Error(
            "class=>method can only be specified with static methods.",
            r"\"class=>method\" can only be specified with static methods\.",
        ),
        Error(
            'The parameter name can be omitted only if the method has only one non-optional IMPORTING parameter or one optional IMPORTING parameter identified by "PREFERRED PARAMETER".',
            r"The parameter name can be omitted only if the method has only one non-optional IMPORTING parameter or one optional IMPORTING parameter identified by \"PREFERRED PARAMETER\".",
        ),
        Error(
            "Instances of the abstract class x cannot be generated.",
            r"Instances of the abstract class .* cannot be generated\.",
        ),
        Error(
            "An instance of the class x cannot be created outside the class.",
            r"An instance of the class .* cannot be created outside the class.",
        ),
        Error(
            "The data object x does not have a component called y.",
            r"The data object .* does not have a component called .*\.",
        ),
        Error(
            "Class x does not contain an interface y.",
            r"Class .* does not contain an interface .*\.",
        ),
        Error(
            "Only static methods can be specified using the short form (method) within a static method.",
            r"Only static methods can be specified using the short form \(method\) within a static method.",
        ),
        Error(
            "Within a static method, only static attributes can be accessed without specifying further information.",
            r"Within a static method, only static attributes can be accessed without specifying further information.",
        ),
        Error(
            "Cannot define global class inside another class",
            r"You may not define the global class .* in class .*",
        ),
        Error(
            "Unsupported TYPE/DECIMALS in OO",
            r"The additions TYPE and DECIMALS are no longer supported in the OO context.*",
        ),
        Error(
            "READ-ONLY only allowed for public attributes",
            r"The addition READ-ONLY is only allowed for the public attributes.*",
        ),
        Error(
            "CLASS_CONSTRUCTOR must be PUBLIC",
            r"\"CLASS_CONSTRUCTOR\" must always be PUBLIC\.",
        ),
        Error(
            "Untyped field symbols not allowed in OO",
            r"Untyped field symbols are not supported in the OO context.*",
        ),
        Error(
            "Tables with headers are no longer supported in the OO context.",
            r"Tables with headers are no longer supported in the OO context\.",
        ),
        Error(
            "The addition OCCURS is no longer supported in the OO context.",
            r"The addition OCCURS is no longer supported in the OO context.*",
        ),
        Error(
            "RETURNING parameter not allowed in database procedure method.",
            r"The method \".*\" contains a database procedure, which means that \".*\" cannot be defined as a RETURNING parameter\.",
        ),
        Error(
            "Implicit keys no longer supported in OO context.",
            r"Keys can no longer be specified implicitly in the OO context.*",
        ),
        Error(
            "Constructor visibility too specific for instance creator.",
            r"Visibility of the constructor cannot be more specific than the visibility of the instance creator.*",
        ),
        Error(
            "Method result must be an object or data reference.",
            r"The result of the method \".*\" must be an object reference or data reference\.",
        ),
    ],
    "Table and Data Structure Errors": [
        Error("x is not an internal table.", r"\".*\" is not an internal table."),
        Error(
            "The key is not specified in full. Types specified generically are completed only in standard tables.",
            r"The key is not specified in full. Types specified generically are completed only in standard tables.",
        ),
        Error(
            "x cannot be converted to the row type of y.",
            r".* cannot be converted to the row type of .*",
        ),
        Error(
            "Only tables with a character-like row type (data type C, N, D, T, or STRING) are allowed with the addition x.",
            r"Only tables with a character-like row type \(data type C, N, D, T, or STRING\) are allowed with the addition .*\.",
        ),
        Error(
            "UNIQUE can only be specified with the table categories HASHED and SORTED.",
            r"UNIQUE can only be specified with the table categories HASHED and SORTED\.",
        ),
        Error(
            "x does not have the structure of a selection table.",
            r".* does not have the structure of a selection table.",
        ),
        Error(
            "Invalid syntax for a table row selection.",
            r"Invalid syntax for a table row selection.",
        ),
        Error(
            "Explicit or implicit index operations cannot be used on tables with type x",
            r"Explicit or implicit index operations cannot be used on tables with types.*\.",
        ),
        Error(
            "Substrings cannot be accessed in internal tables, deep structures, or references.",
            r"Substrings cannot be accessed in internal tables, deep structures, or references\.",
        ),
        Error(
            "Structure or internal table expected",
            r"\".*\" is not a structure or an internal table\.",
        ),
        Error(
            "SORT not supported for SORTED tables",
            r"\".*\" is a table of the type SORTED\. The SORT command cannot be used with this type of table\.",
        ),
        Error(
            "Primary key definition expected",
            r"A primary key of the form .* is expected\.",
        ),
        Error(
            "Table x does not have a key y.",
            r"Table \".*\" does not have a key \".*\"\.",
        ),
        Error(
            "Table cannot be modified within a LOOP across itself.",
            r"The table \".*\" cannot be deleted or overwritten within a LOOP across itself\.",
        ),
        Error(
            "Header line required for internal table.",
            r"The internal table \".*\" does not have a header line; work area must be specified explicitly \(\"FROM wa\"\)\.",
        ),
        Error(
            "Table must be STANDARD and without secondary keys.",
            r"In this statement, the internal table \".*\" must have the type \"STANDARD TABLE\" and cannot have any secondary keys\.",
        ),
    ],
    "Parameter and Method Call Errors": [
        Error(
            "A x parameter must be fully typed.", r"A .* parameter must be fully typed."
        ),
        Error(
            "Returning parameters must be passed as value.",
            r"RETURNING parameters must be specified to be passed as VALUE().",
        ),
        Error(
            "The method does not have a returning parameter.",
            r"The method .* does not have a RETURNING parameter",
        ),
        Error(
            "The generic types cannot be specified in returning parameters.",
            r"The generic types .* cannot be specified in RETURNING parameters.",
        ),
        Error("Method does not exist.", r"Method .* does not exist."),
        Error(
            "Type definition can only be specified once.",
            r"The addition \"... TYPE type\" can only be specified once.",
        ),
        Error(
            "x is not type-compatible with formal parameter y.",
            r".* is not type-compatible with formal parameter .*\.",
        ),
        Error(
            "The formal parameter x does not exist.",
            r"The formal parameter .* does not exist\.",
        ),
        Error(
            "The formal parameter x is a y parameter, not a z parameter.",
            r"The formal parameter .* is a .* parameter, not a .* parameter.",
        ),
        Error(
            "Preferred parameter must be listed as IMPORTING",
            r"The parameter .* specified in the addition PREFERRED PARAMETER is not listed as an IMPORTING parameter\.",
        ),
        Error(
            "Method does not have parameters",
            r"Method \".*\" does not have any parameters\.",
        ),
        Error(
            "No value was passed to the mandatory parameter.",
            r"No value was passed to the mandatory parameter \".*\"\.",
        ),
        Error(
            "IS SUPPLIED only works with optional parameters.",
            r"The \"IS SUPPLIED\" query works only for optional parameters\.",
        ),
    ],
    "Expression and Calculation Errors": [
        Error(
            "x is not a permitted operator in this position of the calculation expression.",
            r".* is not a permitted operator in this position of the calculation expression\.",
        ),
        Error(
            "Error in arithmetic expression",
            r"Error in arithmetic expression.*",
        ),
        Error(
            "Error in logical expression.",
            r"Error in logical expression.*",
        ),
        Error("x cannot be modified.", r"\".*\" cannot be modified."),
        Error(
            "A Boolean expression was expected in x.",
            r"A Boolean expression was expected in .*\.",
        ),
        Error(
            "Relational operator x is not supported.",
            r"Relational operator .* is not supported.",
        ),
        Error(
            "Arithmetic expression cannot be compared with non-numeric operand",
            r"An arithmetic expression cannot be compared with the non-numeric operand \".*\"\.",
        ),
        Error(
            "Arithmetic calculation not permitted",
            r"Arithmetic calculation not permitted here\.",
        ),
    ],
    "String and Text-Related Errors": [
        Error(
            "Multiline literal are not allowed.",
            r"Literals across more than one line are not allowed.",
        ),
        Error(
            "Invalid line break in string template.",
            r"Invalid line break in string template.",
        ),
        Error(
            "Text literal is too long.",
            r"The text literal .* is longer than 255 characters. Check whether it ends correctly.",
        ),
        Error(
            "Format directive unknown or invalid",
            r"Format directive \".*\" (cannot be applied|unknown)\.",
        ),
        Error(
            "Invalid regular expression",
            r"Regular expression \'.*\' is invalid in character position \d+\.",
        ),
        Error("Unknown format specifier", r"Format \".*\" unknown\."),
        Error(
            "MATCH LINE, MATCH OFFSET, and MATCH LENGTH cannot be used with RESULTS.",
            r"The additions MATCH LINE, MATCH OFFSET, and MATCH LENGTH cannot be used with RESULTS\.",
        ),
        Error(
            "ALL OCCURRENCES requires at least one return value.",
            r"The addition ALL OCCURRENCES requires at least one return value to be queried\.",
        ),
        Error(
            "ALPHA format directive cannot be applied to embedded expression.",
            r"Format directive \"ALPHA\" cannot be applied to the embedded expression\.",
        ),
    ],
    "Database and SQL Errors": [
        Error(
            "AMDP: Only elementary or table-like IMPORTING parameters allowed with RETURNING.",
            r"In AMDP methods, only elementary or table-like IMPORTING parameters are allowed in combination with RETURNING.*",
        ),
        Error(
            "AMDP class must implement IF_AMDP_MARKER_HDB.",
            r"Database procedures managed by ABAP can only be defined in classes that implement the marker interface \"IF_AMDP_MARKER_HDB\"\.",
        ),
        Error("SQLSCRIPT:", r"SQLSCRIPT:.*"),
        Error(
            "The INTO/APPENDING clause must be at the end of the SELECT.",
            r"The INTO/APPENDING clause must be at the end of the SELECT.*",
        ),
        Error(
            'The ABAP Dictionary structure or table "LT_CANDIDATE_IDS" is either not active or does not exist.',
            r"The ABAP Dictionary structure or table .* is either not active or does not exist.",
        ),
        Error(
            "Missing FROM in DML statement",
            r"The addition \"FROM\" for DELETE, INSERT, MODIFY, or UPDATE is missing\.",
        ),
        Error(
            "Missing INTO clause in SELECT",
            r"Field list without INTO clause is not allowed\.",
        ),
        Error(
            "Missing INTO/ASSIGNING in SELECT",
            r"Specify one of the additions \"INTO wa\", \"ASSIGNING\", \"REFERENCE INTO\", or \"TRANSPORTING NO FIELDS\"\.",
        ),
        Error(
            "Missing ORDER BY before OFFSET",
            r"If an OFFSET addition exists, an ORDER BY clause must also be specified.*",
        ),
        Error(
            "Table is not defined in the ABAP Dictionary.",
            r"\".*\" is not declared as a table, projection view, or database view in ABAP Dictionary or does not exist in an active version\.",
        ),
        Error(
            "INTO clause required for target area.",
            r"A target area must be specified using an INTO clause\.",
        ),
        Error(
            "Work area has fewer fields than selected.",
            r"The work area \".*\" has fewer fields than selected\.",
        ),
    ],
    "Control Flow Errors": [
        Error(
            "x is allowed only within loops (DO, WHILE, LOOP, SELECT).",
            r".* is allowed only within loops \(DO, WHILE, LOOP, SELECT\)\.",
        ),
        Error(
            "Missing INTO/ASSIGNING in LOOP AT",
            r"In \"LOOP AT .*\", one of the additions .* is required in the .* context\.",
        ),
        Error(
            "INDEX not allowed with generic INSERT INTO TABLE",
            r"INDEX cannot be specified with a generic INSERT statement \(addition \"INTO TABLE\"\)\.",
        ),
        Error("Missing open IF statement", r"No open \"IF\" statement exists\."),
    ],
    "Miscellaneous and Formatting Errors": [
        Error(
            "Unknown predefined function", r"Predefined function \".*\" is unknown\."
        ),
        Error(
            "WRITE TO does not support formatting",
            r"WRITE TO cannot specify any positions, lengths, or formats.*",
        ),
        Error(
            "Message class must be specified correctly",
            r"The message class must either be in parentheses after the number or specified using the addition \"MESSAGE-ID\".*",
        ),
        Error("Other", r".*"),
    ],
}
