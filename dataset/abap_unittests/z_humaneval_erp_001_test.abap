CLASS ltcl_test_find_employees DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS:
      setup,
      teardown,
      test_employees_wo_subordinates FOR TESTING,
      test_all_have_subordinates FOR TESTING,
      test_empty_tables FOR TESTING,
      test_single_employee_no_struct FOR TESTING,
      test_circular_hierarchy FOR TESTING,
      test_multiple_levels FOR TESTING.

    DATA: lt_emp_master_backup    TYPE TABLE OF zemp_master,
          lt_org_structure_backup TYPE TABLE OF zorg_structure.
ENDCLASS.

CLASS ltcl_test_find_employees IMPLEMENTATION.

  METHOD setup.
    " Backup existing data
    SELECT * FROM zemp_master INTO TABLE lt_emp_master_backup.
    SELECT * FROM zorg_structure INTO TABLE lt_org_structure_backup.

    " Clear tables for clean testing
    DELETE FROM zemp_master.
    DELETE FROM zorg_structure.
  ENDMETHOD.

  METHOD teardown.
    " Clean up test data
    DELETE FROM zemp_master.
    DELETE FROM zorg_structure.

    " Restore original data
    IF lines( lt_emp_master_backup ) > 0.
      INSERT zemp_master FROM TABLE lt_emp_master_backup.
    ENDIF.
    IF lines( lt_org_structure_backup ) > 0.
      INSERT zorg_structure FROM TABLE lt_org_structure_backup.
    ENDIF.
  ENDMETHOD.

  METHOD test_employees_wo_subordinates.
    " Test case from the original example
    DATA: lt_expected TYPE stringtab,
          lt_actual   TYPE stringtab.

    " Setup test data
    DATA: lt_emp_data TYPE TABLE OF zemp_master,
          ls_emp_data TYPE zemp_master,
          lt_org_data TYPE TABLE OF zorg_structure,
          ls_org_data TYPE zorg_structure.

    " Insert employee master data
    ls_emp_data-employee_id = 'A'. ls_emp_data-name = 'Anna'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'B'. ls_emp_data-name = 'Boris'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'C'. ls_emp_data-name = 'Carla'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'D'. ls_emp_data-name = 'David'. APPEND ls_emp_data TO lt_emp_data.
    INSERT zemp_master FROM TABLE lt_emp_data.

    " Insert organizational structure data
    ls_org_data-employee_id = 'A'. ls_org_data-supervisor_id = 'B'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'C'. ls_org_data-supervisor_id = 'B'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'B'. ls_org_data-supervisor_id = 'D'. APPEND ls_org_data TO lt_org_data.
    INSERT zorg_structure FROM TABLE lt_org_data.

    " Expected results: Anna and Carla (they don't supervise anyone)
    APPEND 'Anna' TO lt_expected.
    APPEND 'Carla' TO lt_expected.

    " Execute method
    lt_actual = z_humaneval_erp_001=>find_employees_wo_subordinates( ).

    " Sort both tables for comparison
    SORT lt_expected.
    SORT lt_actual.

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lt_actual
      exp = lt_expected
      msg = 'Should return Anna and Carla as employees without subordinates'
    ).
  ENDMETHOD.

  METHOD test_all_have_subordinates.
    " Test case where all employees have subordinates
    DATA: lt_expected TYPE stringtab,
          lt_actual   TYPE stringtab.

    " Setup test data - everyone is a supervisor
    DATA: lt_emp_data TYPE TABLE OF zemp_master,
          ls_emp_data TYPE zemp_master,
          lt_org_data TYPE TABLE OF zorg_structure,
          ls_org_data TYPE zorg_structure.

    " Insert employee master data
    ls_emp_data-employee_id = 'A'. ls_emp_data-name = 'Alice'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'B'. ls_emp_data-name = 'Bob'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'C'. ls_emp_data-name = 'Charlie'. APPEND ls_emp_data TO lt_emp_data.
    INSERT zemp_master FROM TABLE lt_emp_data.

    " Insert organizational structure data
    ls_org_data-employee_id = 'B'. ls_org_data-supervisor_id = 'A'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'C'. ls_org_data-supervisor_id = 'B'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'A'. ls_org_data-supervisor_id = 'C'. APPEND ls_org_data TO lt_org_data.
    INSERT zorg_structure FROM TABLE lt_org_data.

    " Expected: empty table
    CLEAR lt_expected.

    " Execute method
    lt_actual = z_humaneval_erp_001=>find_employees_wo_subordinates( ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lt_actual
      exp = lt_expected
      msg = 'Should return empty table when all employees have subordinates'
    ).
  ENDMETHOD.

  METHOD test_empty_tables.
    " Test with empty database tables
    DATA: lt_expected TYPE stringtab,
          lt_actual   TYPE stringtab.

    " Tables are already empty from setup
    " Expected: empty table
    CLEAR lt_expected.

    " Execute method
    lt_actual = z_humaneval_erp_001=>find_employees_wo_subordinates( ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lt_actual
      exp = lt_expected
      msg = 'Should return empty table when database tables are empty'
    ).
  ENDMETHOD.

  METHOD test_single_employee_no_struct.
    " Test with single employee and no organizational structure
    DATA: lt_expected TYPE stringtab,
          lt_actual   TYPE stringtab.

    " Setup test data
    DATA: ls_emp_data TYPE zemp_master.

    ls_emp_data-employee_id = 'X'.
    ls_emp_data-name = 'Xavier'.
    INSERT zemp_master FROM ls_emp_data.
    " No organizational structure entries

    " Expected: Xavier (no subordinates)
    APPEND 'Xavier' TO lt_expected.

    " Execute method
    lt_actual = z_humaneval_erp_001=>find_employees_wo_subordinates( ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lt_actual
      exp = lt_expected
      msg = 'Should return single employee when no org structure exists'
    ).
  ENDMETHOD.

  METHOD test_circular_hierarchy.
    " Test with circular hierarchy (edge case)
    DATA: lt_expected TYPE stringtab,
          lt_actual   TYPE stringtab.

    " Setup test data with circular reference
    DATA: lt_emp_data TYPE TABLE OF zemp_master,
          ls_emp_data TYPE zemp_master,
          lt_org_data TYPE TABLE OF zorg_structure,
          ls_org_data TYPE zorg_structure.

    " Insert employee master data
    ls_emp_data-employee_id = 'P'. ls_emp_data-name = 'Peter'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'Q'. ls_emp_data-name = 'Queen'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'R'. ls_emp_data-name = 'Robert'. APPEND ls_emp_data TO lt_emp_data.
    INSERT zemp_master FROM TABLE lt_emp_data.

    " Insert organizational structure data with circular reference
    ls_org_data-employee_id = 'Q'. ls_org_data-supervisor_id = 'P'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'R'. ls_org_data-supervisor_id = 'Q'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'P'. ls_org_data-supervisor_id = 'R'. APPEND ls_org_data TO lt_org_data.
    INSERT zorg_structure FROM TABLE lt_org_data.

    " Expected: empty (all are supervisors despite circular reference)
    CLEAR lt_expected.

    " Execute method
    lt_actual = z_humaneval_erp_001=>find_employees_wo_subordinates( ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lt_actual
      exp = lt_expected
      msg = 'Should handle circular hierarchy correctly'
    ).
  ENDMETHOD.

  METHOD test_multiple_levels.
    " Test with multiple levels of hierarchy
    DATA: lt_expected TYPE stringtab,
          lt_actual   TYPE stringtab.

    " Setup test data - 3 level hierarchy
    DATA: lt_emp_data TYPE TABLE OF zemp_master,
          ls_emp_data TYPE zemp_master,
          lt_org_data TYPE TABLE OF zorg_structure,
          ls_org_data TYPE zorg_structure.

    " Insert employee master data
    ls_emp_data-employee_id = 'CEO'. ls_emp_data-name = 'Chief Executive'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'MGR1'. ls_emp_data-name = 'Manager One'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'MGR2'. ls_emp_data-name = 'Manager Two'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'EMP1'. ls_emp_data-name = 'Employee One'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'EMP2'. ls_emp_data-name = 'Employee Two'. APPEND ls_emp_data TO lt_emp_data.
    ls_emp_data-employee_id = 'EMP3'. ls_emp_data-name = 'Employee Three'. APPEND ls_emp_data TO lt_emp_data.
    INSERT zemp_master FROM TABLE lt_emp_data.

    " Insert organizational structure data
    ls_org_data-employee_id = 'MGR1'. ls_org_data-supervisor_id = 'CEO'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'MGR2'. ls_org_data-supervisor_id = 'CEO'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'EMP1'. ls_org_data-supervisor_id = 'MGR1'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'EMP2'. ls_org_data-supervisor_id = 'MGR1'. APPEND ls_org_data TO lt_org_data.
    ls_org_data-employee_id = 'EMP3'. ls_org_data-supervisor_id = 'MGR2'. APPEND ls_org_data TO lt_org_data.
    INSERT zorg_structure FROM TABLE lt_org_data.

    " Expected: EMP1, EMP2, EMP3 (leaf nodes)
    APPEND 'Employee One' TO lt_expected.
    APPEND 'Employee Two' TO lt_expected.
    APPEND 'Employee Three' TO lt_expected.

    " Execute method
    lt_actual = z_humaneval_erp_001=>find_employees_wo_subordinates( ).

    " Sort both tables for comparison
    SORT lt_expected.
    SORT lt_actual.

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lt_actual
      exp = lt_expected
      msg = 'Should return all leaf employees in multi-level hierarchy'
    ).
  ENDMETHOD.

ENDCLASS.