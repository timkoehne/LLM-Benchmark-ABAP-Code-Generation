CLASS ltcl_hierarchy_tests DEFINITION
  FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS:
      setup,
      teardown,
      test_valid_simple_hierarchy FOR TESTING,
      test_valid_complex_hierarchy FOR TESTING,
      test_empty_table FOR TESTING,
      test_multiple_managers FOR TESTING,
      test_no_ceo FOR TESTING,
      test_multiple_ceos FOR TESTING,
      test_cycle_direct FOR TESTING,
      test_cycle_indirect FOR TESTING,
      test_disconnected_employee FOR TESTING,
      test_single_employee_no_mgr FOR TESTING,
      test_self_reference FOR TESTING,
      test_orphaned_manager FOR TESTING.

ENDCLASS.

CLASS ltcl_hierarchy_tests IMPLEMENTATION.

  METHOD setup.
    " Clean up table before each test
    DELETE FROM zorg_structure.
  ENDMETHOD.

  METHOD teardown.
    " Clean up table after each test
    DELETE FROM zorg_structure.
  ENDMETHOD.

  METHOD test_valid_simple_hierarchy.
    " Test case: A->B->C->D (valid hierarchy)
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'B' )
      ( employee_id = 'B' supervisor_id = 'C' )
      ( employee_id = 'C' supervisor_id = 'D' )
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_true(
      act = lv_result
      msg = 'Simple valid hierarchy should return true'
    ).
  ENDMETHOD.

  METHOD test_valid_complex_hierarchy.
    " Test case: Complex hierarchy with multiple branches
    "     CEO
    "    /   \
    "   MGR1 MGR2
    "  /  |   |  \
    " A   B   C   D
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'MGR1' )
      ( employee_id = 'B' supervisor_id = 'MGR1' )
      ( employee_id = 'C' supervisor_id = 'MGR2' )
      ( employee_id = 'D' supervisor_id = 'MGR2' )
      ( employee_id = 'MGR1' supervisor_id = 'CEO' )
      ( employee_id = 'MGR2' supervisor_id = 'CEO' )
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_true(
      act = lv_result
      msg = 'Complex valid hierarchy should return true'
    ).
  ENDMETHOD.

  METHOD test_empty_table.
    " Test case: Empty table
    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Empty table should return false'
    ).
  ENDMETHOD.

  METHOD test_multiple_managers.
    " Test case: Employee has multiple managers (duplicate employee_id)
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'B' )
      ( employee_id = 'A' supervisor_id = 'C' )  " A has two managers
      ( employee_id = 'B' supervisor_id = 'CEO' )
      ( employee_id = 'C' supervisor_id = 'CEO' )
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Employee with multiple managers should return false'
    ).
  ENDMETHOD.

  METHOD test_no_ceo.
    " Test case: No CEO (everyone has a manager)
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'B' )
      ( employee_id = 'B' supervisor_id = 'A' )  " Cycle, no CEO
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Structure with no CEO should return false'
    ).
  ENDMETHOD.

  METHOD test_multiple_ceos.
    " Test case: Multiple CEOs (disconnected hierarchies)
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'CEO1' )
      ( employee_id = 'B' supervisor_id = 'CEO2' )  " Two separate hierarchies
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Structure with multiple CEOs should return false'
    ).
  ENDMETHOD.

  METHOD test_cycle_direct.
    " Test case: Direct cycle (A->B->A)
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'B' )
      ( employee_id = 'B' supervisor_id = 'A' )
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Direct cycle should return false'
    ).
  ENDMETHOD.

  METHOD test_cycle_indirect.
    " Test case: Indirect cycle (A->B->C->A)
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'B' )
      ( employee_id = 'B' supervisor_id = 'C' )
      ( employee_id = 'C' supervisor_id = 'A' )
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Indirect cycle should return false'
    ).
  ENDMETHOD.

  METHOD test_disconnected_employee.
    " Test case: Employee not connected to main hierarchy
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'CEO' )
      ( employee_id = 'B' supervisor_id = 'OTHERBOSS' )  " B is disconnected
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Disconnected employee should return false'
    ).
  ENDMETHOD.

  METHOD test_single_employee_no_mgr.
    " Test case: Single person with no manager (valid CEO)
    " This should be invalid as there are no employees, only a CEO
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    " No entries - CEO exists but has no subordinates
    " This case is handled by empty table test

    " Alternative: CEO manages himself (self-reference)
    lt_test_data = VALUE #(
      ( employee_id = 'CEO' supervisor_id = 'CEO' )
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Self-managing CEO should return false'
    ).
  ENDMETHOD.

  METHOD test_self_reference.
    " Test case: Employee manages themselves
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'A' )  " Self-reference
      ( employee_id = 'B' supervisor_id = 'CEO' )
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Self-reference should return false'
    ).
  ENDMETHOD.

  METHOD test_orphaned_manager.
    " Test case: Manager who is referenced but not in employee list
    DATA: lt_test_data TYPE TABLE OF zorg_structure.

    lt_test_data = VALUE #(
      ( employee_id = 'A' supervisor_id = 'MISSING_MGR' )
      ( employee_id = 'B' supervisor_id = 'CEO' )
    ).

    INSERT zorg_structure FROM TABLE lt_test_data.

    DATA(lv_result) = z_humaneval_erp_004=>is_valid_hierarchy( ).

    cl_abap_unit_assert=>assert_false(
      act = lv_result
      msg = 'Orphaned manager reference should return false'
    ).
  ENDMETHOD.

ENDCLASS.