CLASS z_humaneval_erp_001 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.

    CLASS-METHODS: find_employees_wo_subordinates
      RETURNING VALUE(rt_employee_names) TYPE stringtab.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.

CLASS z_humaneval_erp_001 IMPLEMENTATION.
  METHOD find_employees_wo_subordinates.

    " Internal table to store results
    DATA: lt_results TYPE TABLE OF string.

    " Select employees who are not supervisors
    " Use LEFT OUTER JOIN to find employees without subordinates
    SELECT em~name
      FROM zemp_master AS em
      LEFT OUTER JOIN zorg_structure AS os
        ON em~employee_id = os~supervisor_id
      WHERE os~supervisor_id IS NULL
      INTO TABLE @lt_results.

    " Return the results
    rt_employee_names = lt_results.

  ENDMETHOD.
ENDCLASS.