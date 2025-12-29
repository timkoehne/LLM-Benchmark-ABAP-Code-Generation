CLASS z_humaneval_erp_000 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.
    CLASS-METHODS: find_ceo_name
      RETURNING VALUE(rv_ceo_name) TYPE string.

  PRIVATE SECTION.

ENDCLASS.

CLASS z_humaneval_erp_000 IMPLEMENTATION.

  METHOD find_ceo_name.

    DATA: lt_employees      TYPE TABLE OF zemp_master,
          lt_org_structure  TYPE TABLE OF zorg_structure,
          lt_supervised_ids TYPE TABLE OF zorg_structure-employee_id,
          lv_ceo_id         TYPE zemp_master-employee_id.

    CLEAR: rv_ceo_name.

    " Get all employees
    SELECT * FROM zemp_master INTO TABLE lt_employees.

    " Check if we have any employees
    IF lines( lt_employees ) = 0.
      RETURN. " No employees, no CEO
    ENDIF.

    " Get all organizational relationships
    SELECT * FROM zorg_structure INTO TABLE lt_org_structure.

    " If no organizational structure exists, we can't determine CEO
    IF lines( lt_org_structure ) = 0.
      " Special case: if only one employee exists, they could be CEO
      IF lines( lt_employees ) = 1.
        READ TABLE lt_employees INTO DATA(ls_employee) INDEX 1.
        rv_ceo_name = ls_employee-name.
      ENDIF.
      RETURN.
    ENDIF.

    " Collect all employee IDs that have supervisors (are supervised by someone)
    LOOP AT lt_org_structure INTO DATA(ls_org).
      APPEND ls_org-employee_id TO lt_supervised_ids.
    ENDLOOP.

    " Find employees who are NOT in the supervised list (potential CEOs)
    DATA: lt_potential_ceos TYPE TABLE OF zemp_master-employee_id.

    LOOP AT lt_employees INTO ls_employee.
      READ TABLE lt_supervised_ids TRANSPORTING NO FIELDS
           WITH KEY table_line = ls_employee-employee_id.
      IF sy-subrc <> 0. " Employee not found in supervised list
        APPEND ls_employee-employee_id TO lt_potential_ceos.
      ENDIF.
    ENDLOOP.

    " There should be exactly one CEO
    IF lines( lt_potential_ceos ) = 1.
      READ TABLE lt_potential_ceos INTO lv_ceo_id INDEX 1.

      " Get the CEO's name
      READ TABLE lt_employees INTO ls_employee
           WITH KEY employee_id = lv_ceo_id.
      IF sy-subrc = 0.
        rv_ceo_name = ls_employee-name.
      ENDIF.
    ENDIF.

    " If we have 0 or multiple potential CEOs, return empty (ambiguous structure)

  ENDMETHOD.

ENDCLASS.