CLASS ltcl_test_critical_path DEFINITION
  FINAL
  FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS:
      setup,
      teardown,
      test_example_case FOR TESTING,
      test_single_step FOR TESTING,
      test_parallel_paths FOR TESTING,
      test_empty_tables FOR TESTING,
      test_linear_sequence FOR TESTING.

ENDCLASS.

CLASS ltcl_test_critical_path IMPLEMENTATION.

  METHOD setup.
    " Clean up tables before each test
    DELETE FROM zfs_data.
    DELETE FROM zfnet_data.
    COMMIT WORK.
  ENDMETHOD.

  METHOD teardown.
    " Clean up tables after each test
    DELETE FROM zfs_data.
    DELETE FROM zfnet_data.
    COMMIT WORK.
  ENDMETHOD.

  METHOD test_example_case.
    " Test the original example case
    " Expected critical path: A2->A4->A6 = 3+3+1 = 7

    " Insert test data for steps
    DATA: lt_steps TYPE TABLE OF zfs_data,
          lt_deps  TYPE TABLE OF zfnet_data.

    lt_steps = VALUE #(
      ( step_id = 'A1' description = 'Turning'     duration = 2 )
      ( step_id = 'A2' description = 'Assembling'  duration = 3 )
      ( step_id = 'A3' description = 'Milling'     duration = 1 )
      ( step_id = 'A4' description = 'Painting'    duration = 3 )
      ( step_id = 'A5' description = 'Cleaning'    duration = 1 )
      ( step_id = 'A6' description = 'Packaging'   duration = 1 )
    ).
    MODIFY zfs_data FROM TABLE lt_steps.

    " Insert test data for dependencies
    lt_deps = VALUE #(
      ( from_step = 'A1' to_step = 'A4' )
      ( from_step = 'A2' to_step = 'A4' )
      ( from_step = 'A3' to_step = 'A5' )
      ( from_step = 'A4' to_step = 'A6' )
      ( from_step = 'A5' to_step = 'A6' )
    ).
    INSERT zfnet_data FROM TABLE lt_deps.

    COMMIT WORK.

    " Execute the method under test
    DATA(lv_result) = z_humaneval_erp_005=>calculate_critical_path( ).

    " Assert the result
    cl_abap_unit_assert=>assert_equals(
      act = lv_result
      exp = 7
      msg = 'Critical path duration should be 7 for example case'
    ).
  ENDMETHOD.

  METHOD test_single_step.
    " Test with only one step
    " Expected result: duration of the single step

    " Insert single step
    DATA: lt_steps TYPE TABLE OF zfs_data.

    lt_steps = VALUE #(
      ( step_id = 'S1' description = 'Single Step' duration = 5 )
    ).
    MODIFY zfs_data FROM TABLE lt_steps.

    COMMIT WORK.

    " Execute the method under test
    DATA(lv_result) = z_humaneval_erp_005=>calculate_critical_path( ).

    " Assert the result
    cl_abap_unit_assert=>assert_equals(
      act = lv_result
      exp = 5
      msg = 'Critical path duration should be 5 for single step'
    ).
  ENDMETHOD.

  METHOD test_parallel_paths.
    " Test with parallel paths of different lengths
    " Path 1: S1->S3 = 2+4 = 6
    " Path 2: S2->S4 = 3+1 = 4
    " Expected critical path: 6

    " Insert test data for steps
    DATA: lt_steps TYPE TABLE OF zfs_data,
          lt_deps  TYPE TABLE OF zfnet_data.

    lt_steps = VALUE #(
      ( step_id = 'S1' description = 'Step 1' duration = 2 )
      ( step_id = 'S2' description = 'Step 2' duration = 3 )
      ( step_id = 'S3' description = 'Step 3' duration = 4 )
      ( step_id = 'S4' description = 'Step 4' duration = 1 )
    ).
    MODIFY zfs_data FROM TABLE lt_steps.

    " Insert test data for dependencies
    lt_deps = VALUE #(
      ( from_step = 'S1' to_step = 'S3' )
      ( from_step = 'S2' to_step = 'S4' )
    ).
    INSERT zfnet_data FROM TABLE lt_deps.

    COMMIT WORK.

    " Execute the method under test
    DATA(lv_result) = z_humaneval_erp_005=>calculate_critical_path( ).

    " Assert the result
    cl_abap_unit_assert=>assert_equals(
      act = lv_result
      exp = 6
      msg = 'Critical path duration should be 6 for parallel paths'
    ).
  ENDMETHOD.

  METHOD test_empty_tables.
    " Test with empty tables
    " Expected result: 0

    " Tables are already empty from setup
    COMMIT WORK.

    " Execute the method under test
    DATA(lv_result) = z_humaneval_erp_005=>calculate_critical_path( ).

    " Assert the result
    cl_abap_unit_assert=>assert_equals(
      act = lv_result
      exp = 0
      msg = 'Critical path duration should be 0 for empty tables'
    ).
  ENDMETHOD.

  METHOD test_linear_sequence.
    " Test with a linear sequence of steps
    " S1->S2->S3->S4 = 1+2+3+4 = 10
    " Expected critical path: 10

    " Insert test data for steps
    DATA: lt_steps TYPE TABLE OF zfs_data,
          lt_deps  TYPE TABLE OF zfnet_data.

    lt_steps = VALUE #(
      ( step_id = 'S1' description = 'Step 1' duration = 1 )
      ( step_id = 'S2' description = 'Step 2' duration = 2 )
      ( step_id = 'S3' description = 'Step 3' duration = 3 )
      ( step_id = 'S4' description = 'Step 4' duration = 4 )
    ).
    MODIFY zfs_data FROM TABLE lt_steps.

    " Insert test data for dependencies (linear chain)
    lt_deps = VALUE #(
      ( from_step = 'S1' to_step = 'S2' )
      ( from_step = 'S2' to_step = 'S3' )
      ( from_step = 'S3' to_step = 'S4' )
    ).
    INSERT zfnet_data FROM TABLE lt_deps.

    COMMIT WORK.

    " Execute the method under test
    DATA(lv_result) = z_humaneval_erp_005=>calculate_critical_path( ).

    " Assert the result
    cl_abap_unit_assert=>assert_equals(
      act = lv_result
      exp = 10
      msg = 'Critical path duration should be 10 for linear sequence'
    ).
  ENDMETHOD.

ENDCLASS.