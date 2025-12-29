CLASS ltcl_test_ceo_finder DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS:
      setup,
      test_normal_hierarchy FOR TESTING,
      test_no_employees FOR TESTING,
      test_single_employee FOR TESTING,
      test_no_org_structure FOR TESTING,
      test_multiple_ceos FOR TESTING,
      test_circular_structure FOR TESTING,
      test_employee_not_in_master FOR TESTING.

ENDCLASS.

CLASS ltcl_test_ceo_finder IMPLEMENTATION.

  METHOD setup.
    DELETE FROM zemp_master.
    DELETE FROM zorg_structure.
    COMMIT WORK.
  ENDMETHOD.


  METHOD test_normal_hierarchy.
    " Test case: Normal hierarchy with clear CEO
    " Alice (CEO) -> Bob -> Charlie

    DATA: lt_employees     TYPE TABLE OF zemp_master,
          lt_org_structure TYPE TABLE OF zorg_structure,
          ls_employee      TYPE zemp_master,
          ls_org           TYPE zorg_structure.

    " Insert test employees
    ls_employee-employee_id = 'A'.
    ls_employee-name = 'Alice'.
    APPEND ls_employee TO lt_employees.

    ls_employee-employee_id = 'B'.
    ls_employee-name = 'Bob'.
    APPEND ls_employee TO lt_employees.

    ls_employee-employee_id = 'C'.
    ls_employee-name = 'Charlie'.
    APPEND ls_employee TO lt_employees.

    INSERT zemp_master FROM TABLE lt_employees.

    " Insert organizational structure
    ls_org-employee_id = 'B'.
    ls_org-supervisor_id = 'A'.
    APPEND ls_org TO lt_org_structure.

    ls_org-employee_id = 'C'.
    ls_org-supervisor_id = 'B'.
    APPEND ls_org TO lt_org_structure.

    INSERT zorg_structure FROM TABLE lt_org_structure.

    " Test the method
    DATA(lv_ceo_name) = z_humaneval_erp_000=>find_ceo_name( ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lv_ceo_name
      exp = 'Alice'
      msg = 'CEO should be Alice in normal hierarchy'
    ).
  ENDMETHOD.

  METHOD test_no_employees.
    " Test case: No employees in the system

    " No data insertion needed - tables are already empty

    " Test the method
    DATA(lv_ceo_name) = z_humaneval_erp_000=>find_ceo_name( ).

    " Assert
    cl_abap_unit_assert=>assert_initial(
      act = lv_ceo_name
      msg = 'CEO should be empty when no employees exist'
    ).
  ENDMETHOD.

  METHOD test_single_employee.
    " Test case: Single employee with no organizational structure

    DATA: lt_employees TYPE TABLE OF zemp_master,
          ls_employee  TYPE zemp_master.

    " Insert single employee
    ls_employee-employee_id = 'A'.
    ls_employee-name = 'Alice'.
    APPEND ls_employee TO lt_employees.

    INSERT zemp_master FROM TABLE lt_employees.

    " Test the method
    DATA(lv_ceo_name) = z_humaneval_erp_000=>find_ceo_name( ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lv_ceo_name
      exp = 'Alice'
      msg = 'Single employee should be CEO'
    ).
  ENDMETHOD.

  METHOD test_no_org_structure.
    " Test case: Multiple employees but no organizational structure

    DATA: lt_employees TYPE TABLE OF zemp_master,
          ls_employee  TYPE zemp_master.

    " Insert multiple employees
    ls_employee-employee_id = 'A'.
    ls_employee-name = 'Alice'.
    APPEND ls_employee TO lt_employees.

    ls_employee-employee_id = 'B'.
    ls_employee-name = 'Bob'.
    APPEND ls_employee TO lt_employees.

    INSERT zemp_master FROM TABLE lt_employees.

    " Test the method
    DATA(lv_ceo_name) = z_humaneval_erp_000=>find_ceo_name( ).

    " Assert
    cl_abap_unit_assert=>assert_initial(
      act = lv_ceo_name
      msg = 'CEO should be empty when multiple employees but no org structure'
    ).
  ENDMETHOD.

  METHOD test_multiple_ceos.
    " Test case: Multiple potential CEOs (ambiguous structure)

    DATA: lt_employees     TYPE TABLE OF zemp_master,
          lt_org_structure TYPE TABLE OF zorg_structure,
          ls_employee      TYPE zemp_master,
          ls_org           TYPE zorg_structure.

    " Insert employees
    ls_employee-employee_id = 'A'.
    ls_employee-name = 'Alice'.
    APPEND ls_employee TO lt_employees.

    ls_employee-employee_id = 'B'.
    ls_employee-name = 'Bob'.
    APPEND ls_employee TO lt_employees.

    ls_employee-employee_id = 'C'.
    ls_employee-name = 'Charlie'.
    APPEND ls_employee TO lt_employees.

    ls_employee-employee_id = 'D'.
    ls_employee-name = 'David'.
    APPEND ls_employee TO lt_employees.

    INSERT zemp_master FROM TABLE lt_employees.

    " Insert organizational structure with two separate hierarchies
    ls_org-employee_id = 'B'.
    ls_org-supervisor_id = 'A'.
    APPEND ls_org TO lt_org_structure.

    ls_org-employee_id = 'D'.
    ls_org-supervisor_id = 'C'.
    APPEND ls_org TO lt_org_structure.

    INSERT zorg_structure FROM TABLE lt_org_structure.



    " Test the method
    DATA(lv_ceo_name) = z_humaneval_erp_000=>find_ceo_name( ).

    " Assert
    cl_abap_unit_assert=>assert_initial(
      act = lv_ceo_name
      msg = 'CEO should be empty when multiple potential CEOs exist'
    ).
  ENDMETHOD.

  METHOD test_circular_structure.
    " Test case: Circular reference (everyone has a supervisor)

    DATA: lt_employees     TYPE TABLE OF zemp_master,
          lt_org_structure TYPE TABLE OF zorg_structure,
          ls_employee      TYPE zemp_master,
          ls_org           TYPE zorg_structure.

    " Insert employees
    ls_employee-employee_id = 'A'.
    ls_employee-name = 'Alice'.
    APPEND ls_employee TO lt_employees.

    ls_employee-employee_id = 'B'.
    ls_employee-name = 'Bob'.
    APPEND ls_employee TO lt_employees.

    INSERT zemp_master FROM TABLE lt_employees.

    " Insert circular organizational structure
    ls_org-employee_id = 'A'.
    ls_org-supervisor_id = 'B'.
    APPEND ls_org TO lt_org_structure.

    ls_org-employee_id = 'B'.
    ls_org-supervisor_id = 'A'.
    APPEND ls_org TO lt_org_structure.

    INSERT zorg_structure FROM TABLE lt_org_structure.

    " Test the method
    DATA(lv_ceo_name) = z_humaneval_erp_000=>find_ceo_name( ).

    " Assert
    cl_abap_unit_assert=>assert_initial(
      act = lv_ceo_name
      msg = 'CEO should be empty in circular structure'
    ).
  ENDMETHOD.

  METHOD test_employee_not_in_master.
    " Test case: Organizational structure references non-existent employee

    DATA: lt_employees     TYPE TABLE OF zemp_master,
          lt_org_structure TYPE TABLE OF zorg_structure,
          ls_employee      TYPE zemp_master,
          ls_org           TYPE zorg_structure.

    " Insert employees
    ls_employee-employee_id = 'A'.
    ls_employee-name = 'Alice'.
    APPEND ls_employee TO lt_employees.

    ls_employee-employee_id = 'B'.
    ls_employee-name = 'Bob'.
    APPEND ls_employee TO lt_employees.

    INSERT zemp_master FROM TABLE lt_employees.

    " Insert organizational structure with reference to non-existent employee
    ls_org-employee_id = 'B'.
    ls_org-supervisor_id = 'A'.
    APPEND ls_org TO lt_org_structure.

    ls_org-employee_id = 'C'.  " C doesn't exist in master
    ls_org-supervisor_id = 'A'.
    APPEND ls_org TO lt_org_structure.

    INSERT zorg_structure FROM TABLE lt_org_structure.

    " Test the method
    DATA(lv_ceo_name) = z_humaneval_erp_000=>find_ceo_name( ).

    " Assert - Alice should still be CEO as she's not supervised
    cl_abap_unit_assert=>assert_equals(
      act = lv_ceo_name
      exp = 'Alice'
      msg = 'CEO should be Alice even with orphaned org structure entries'
    ).
  ENDMETHOD.

ENDCLASS.