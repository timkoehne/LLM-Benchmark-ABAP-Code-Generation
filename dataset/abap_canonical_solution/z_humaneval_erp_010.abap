CLASS z_humaneval_erp_010 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.
    TYPES:
      tt_customer_records TYPE STANDARD TABLE OF zcustomer WITH EMPTY KEY .

    CLASS-METHODS find_by_pattern
      IMPORTING
        iv_pattern        TYPE string
      RETURNING
        VALUE(rt_results) TYPE tt_customer_records.

ENDCLASS.

CLASS z_humaneval_erp_010 IMPLEMENTATION.

  METHOD find_by_pattern.

    DATA: lv_pattern_upper TYPE string.
    DATA: lt_raw_customers TYPE STANDARD TABLE OF zcustomer WITH EMPTY KEY.
    DATA: ls_raw_customer  TYPE zcustomer.

    " 1. Convert the input pattern to uppercase using ABAP's TRANSLATE statement.
    lv_pattern_upper = iv_pattern. " Assign first
    TRANSLATE lv_pattern_upper TO UPPER CASE. " Then translate

    " The CP operator implicitly treats the search pattern as containing leading/trailing wildcards
    " when comparing against an exact string. If you need explicit wildcards for CP,
    " it's slightly different (e.g., '*' for any string).
    " For a simple 'contains' check, the pattern for CP is often just the substring itself.
    " However, to match the behavior of '%' in LIKE, a simple pattern like '*substring*' is needed for CP.

    " To precisely mimic '%' in LIKE, CP uses '*' as a wildcard.
    " So, for 'contains', the pattern for CP should be '*<pattern>*'.
    lv_pattern_upper = '*' && lv_pattern_upper && '*'.


    " 2. Select all customers into an internal table.
    "    This is necessary because direct case-insensitive search with functions
    "    in the WHERE clause is not supported on your system.
    SELECT customer_id, name
      FROM zcustomer
      INTO CORRESPONDING FIELDS OF TABLE @lt_raw_customers.

    " 3. Loop through the raw data and filter/compare in ABAP memory.
    LOOP AT lt_raw_customers INTO ls_raw_customer.
      DATA(lv_customer_id_upper) = ls_raw_customer-customer_id.
      TRANSLATE lv_customer_id_upper TO UPPER CASE.

      DATA(lv_name_upper) = ls_raw_customer-name.
      TRANSLATE lv_name_upper TO UPPER CASE.

      " Now compare the uppercased database values against the uppercased pattern
      " using the CP (Contains Pattern) operator.
      " CP looks for patterns defined with '*' as wildcard.
      IF lv_customer_id_upper CP lv_pattern_upper OR
         lv_name_upper        CP lv_pattern_upper.
        APPEND CORRESPONDING #( ls_raw_customer ) TO rt_results.
      ENDIF.
    ENDLOOP.

  ENDMETHOD.

ENDCLASS.