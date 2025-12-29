CLASS z_humaneval_erp_004 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    CLASS-METHODS: is_valid_hierarchy
      RETURNING VALUE(rv_valid) TYPE abap_bool.

ENDCLASS.

CLASS z_humaneval_erp_004 IMPLEMENTATION.

  METHOD is_valid_hierarchy.
    DATA: lt_org_structure TYPE TABLE OF zorg_structure,
          lt_employees     TYPE SORTED TABLE OF char20 WITH UNIQUE KEY table_line,
          lt_superiors     TYPE SORTED TABLE OF char20 WITH UNIQUE KEY table_line,
          lt_all_persons   TYPE SORTED TABLE OF char20 WITH UNIQUE KEY table_line,
          lt_ceos          TYPE SORTED TABLE OF char20 WITH UNIQUE KEY table_line,
          lv_current       TYPE char20,
          lv_steps         TYPE i,
          lt_visited       TYPE SORTED TABLE OF char20 WITH UNIQUE KEY table_line.

    " Read all entries from ZORG_STRUCTURE
    SELECT * FROM zorg_structure INTO TABLE lt_org_structure.

    " Return false if no data
    IF lines( lt_org_structure ) = 0.
      rv_valid = abap_false.
      RETURN.
    ENDIF.

    " Check 1: Each employee has at most one direct manager
    " Check 2: Collect all persons and find CEO candidates
    LOOP AT lt_org_structure INTO DATA(ls_entry).
      " Skip empty entries
      IF ls_entry-employee_id IS INITIAL.
        rv_valid = abap_false.
        RETURN.
      ENDIF.

      " Check for duplicate employees (multiple managers)
      INSERT ls_entry-employee_id INTO TABLE lt_employees.
      IF sy-subrc <> 0.
        rv_valid = abap_false.
        RETURN.
      ENDIF.

      " Collect all persons
      INSERT ls_entry-employee_id INTO TABLE lt_all_persons.
      IF ls_entry-supervisor_id IS NOT INITIAL.
        INSERT ls_entry-supervisor_id INTO TABLE lt_all_persons.
        INSERT ls_entry-supervisor_id INTO TABLE lt_superiors.
      ENDIF.
    ENDLOOP.

    " Check 3: Find CEOs (persons who are not employees)
    LOOP AT lt_all_persons INTO DATA(lv_person).
      IF NOT line_exists( lt_employees[ table_line = lv_person ] ).
        INSERT lv_person INTO TABLE lt_ceos.
      ENDIF.
    ENDLOOP.

    " Must have exactly one CEO
    IF lines( lt_ceos ) <> 1.
      rv_valid = abap_false.
      RETURN.
    ENDIF.

    READ TABLE lt_ceos INDEX 1 INTO DATA(lv_ceo).

    " Check 4: No cycles and all connected to CEO
    LOOP AT lt_all_persons INTO lv_person.
      CLEAR: lt_visited, lv_current, lv_steps.
      lv_current = lv_person.

      " Trace up the hierarchy
      WHILE lv_current IS NOT INITIAL AND lv_steps < lines( lt_all_persons ).
        " Check for cycles
        IF line_exists( lt_visited[ table_line = lv_current ] ).
          rv_valid = abap_false.
          RETURN.
        ENDIF.
        INSERT lv_current INTO TABLE lt_visited.

        " If we reached the CEO, this person is connected
        IF lv_current = lv_ceo.
          EXIT.
        ENDIF.

        " Find superior
        READ TABLE lt_org_structure INTO ls_entry
          WITH KEY employee_id = lv_current.
        IF sy-subrc = 0.
          lv_current = ls_entry-supervisor_id.
        ELSE.
          " Person is not an employee, check if it's the CEO
          IF lv_current <> lv_ceo.
            rv_valid = abap_false.
            RETURN.
          ENDIF.
          EXIT.
        ENDIF.

        lv_steps = lv_steps + 1.
      ENDWHILE.

      " Check if we ended at CEO or exceeded max steps (cycle)
      IF lv_current <> lv_ceo OR lv_steps >= lines( lt_all_persons ).
        rv_valid = abap_false.
        RETURN.
      ENDIF.
    ENDLOOP.

    rv_valid = abap_true.
  ENDMETHOD.

ENDCLASS.