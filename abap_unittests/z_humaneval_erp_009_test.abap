CLASS ltc_sales_aggregation DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS:
      setup,
      teardown,
      test_basic_aggregation FOR TESTING,
      test_empty_source_table FOR TESTING,
      test_single_entry FOR TESTING,
      test_zero_amounts FOR TESTING,
      test_negative_amounts FOR TESTING,
      test_same_person_diff_articles FOR TESTING,
      test_diff_people_same_article FOR TESTING.

ENDCLASS.

CLASS ltc_sales_aggregation IMPLEMENTATION.

  METHOD setup.
    " Clear tables before each test
    DELETE FROM zsales_positions.
    DELETE FROM zsales_aggr.
    COMMIT WORK.
  ENDMETHOD.

  METHOD teardown.
    " Clean up after each test
    DELETE FROM zsales_positions.
    DELETE FROM zsales_aggr.
    COMMIT WORK.
  ENDMETHOD.

  METHOD test_basic_aggregation.
    " Test the example scenario from requirements
    DATA: lt_expected_result TYPE TABLE OF zsales_aggr,
          lt_actual_result   TYPE TABLE OF zsales_aggr,
          lv_success         TYPE abap_bool.

    " Insert test data directly - Example from requirements
    INSERT zsales_positions FROM TABLE @( VALUE #(
      ( zid = 1 zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '1000.00' )
      ( zid = 2 zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '500.00' )
      ( zid = 3 zname = 'JONES' zarticle = 'MOUSE' zcurrency = 'USD' zrev = '50.00' )
      ( zid = 4 zname = 'JONES' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '800.00' )
    ) ).
    COMMIT WORK.

    " Expected aggregated results
    lt_expected_result = VALUE #(
      ( zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '1500.00' )
      ( zname = 'JONES' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '800.00' )
      ( zname = 'JONES' zarticle = 'MOUSE' zcurrency = 'USD' zrev = '50.00' )
    ).

    " Execute the method
    lv_success = z_humaneval_erp_009=>process_sales_aggregation( ).

    " Verify success
    cl_abap_unit_assert=>assert_true(
      act = lv_success
      msg = 'Aggregation should succeed' ).

    " Read actual results
    SELECT zname, zarticle, zcurrency, zrev
      FROM zsales_aggr
      ORDER BY zname, zarticle
      INTO TABLE @lt_actual_result.

    " Verify results count
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual_result )
      exp = 3
      msg = 'Should have 3 aggregated entries' ).

    " Verify specific entries
    SORT lt_actual_result BY zname zarticle.
    SORT lt_expected_result BY zname zarticle.

    cl_abap_unit_assert=>assert_equals(
      act = lt_actual_result
      exp = lt_expected_result
      msg = 'Aggregated results should match expected values' ).

  ENDMETHOD.

  METHOD test_empty_source_table.
    DATA: lv_success       TYPE abap_bool,
          lt_actual_result TYPE TABLE OF zsales_aggr.

    " Execute with empty source table
    lv_success = z_humaneval_erp_009=>process_sales_aggregation( ).

    " Should still succeed
    cl_abap_unit_assert=>assert_true(
      act = lv_success
      msg = 'Should succeed even with empty source table' ).

    " Result table should be empty
    SELECT * FROM zsales_aggr INTO TABLE @lt_actual_result.
    cl_abap_unit_assert=>assert_initial(
      act = lt_actual_result
      msg = 'Aggregated table should be empty' ).

  ENDMETHOD.

  METHOD test_single_entry.
    DATA: lt_actual_result TYPE TABLE OF zsales_aggr,
          lv_success       TYPE abap_bool.

    " Insert single entry directly
    INSERT zsales_positions FROM @( VALUE zsales_positions(
      zid = 1 zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '1000.00' ) ).
    COMMIT WORK.

    lv_success = z_humaneval_erp_009=>process_sales_aggregation( ).

    cl_abap_unit_assert=>assert_true(
      act = lv_success
      msg = 'Single entry aggregation should succeed' ).

    SELECT * FROM zsales_aggr INTO TABLE @lt_actual_result.

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual_result )
      exp = 1
      msg = 'Should have exactly 1 entry' ).

    READ TABLE lt_actual_result INDEX 1 INTO DATA(ls_result).
    cl_abap_unit_assert=>assert_equals(
      act = ls_result-zrev
      exp = '1000.00'
      msg = 'Amount should be preserved' ).

  ENDMETHOD.

  METHOD test_zero_amounts.
    DATA: lt_actual_result TYPE TABLE OF zsales_aggr,
          lv_success       TYPE abap_bool.

    INSERT zsales_positions FROM TABLE @( VALUE #(
      ( zid = 1 zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '1000.00' )
      ( zid = 2 zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '0.00' )
    ) ).
    COMMIT WORK.

    lv_success = z_humaneval_erp_009=>process_sales_aggregation( ).

    cl_abap_unit_assert=>assert_true( act = lv_success ).

    SELECT * FROM zsales_aggr INTO TABLE @lt_actual_result.
    READ TABLE lt_actual_result INDEX 1 INTO DATA(ls_result).

    cl_abap_unit_assert=>assert_equals(
      act = ls_result-zrev
      exp = '1000.00'
      msg = 'Zero amounts should be handled correctly' ).

  ENDMETHOD.

  METHOD test_negative_amounts.
    DATA: lt_actual_result TYPE TABLE OF zsales_aggr,
          lv_success       TYPE abap_bool.

    " Test with returns/refunds (negative amounts)
    INSERT zsales_positions FROM TABLE @( VALUE #(
      ( zid = 1 zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '1000.00' )
      ( zid = 2 zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '-200.00' )
    ) ).
    COMMIT WORK.

    lv_success = z_humaneval_erp_009=>process_sales_aggregation( ).

    cl_abap_unit_assert=>assert_true( act = lv_success ).

    SELECT * FROM zsales_aggr INTO TABLE @lt_actual_result.
    READ TABLE lt_actual_result INDEX 1 INTO DATA(ls_result).

    cl_abap_unit_assert=>assert_equals(
      act = ls_result-zrev
      exp = '800.00'
      msg = 'Negative amounts should be subtracted correctly' ).

  ENDMETHOD.

  METHOD test_same_person_diff_articles.
    DATA: lt_actual_result TYPE TABLE OF zsales_aggr,
          lv_success       TYPE abap_bool.

    INSERT zsales_positions FROM TABLE @( VALUE #(
      ( zid = 1 zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '1000.00' )
      ( zid = 2 zname = 'SMITH' zarticle = 'MOUSE' zcurrency = 'USD' zrev = '50.00' )
      ( zid = 3 zname = 'SMITH' zarticle = 'KEYBOARD' zcurrency = 'USD' zrev = '100.00' )
    ) ).
    COMMIT WORK.

    lv_success = z_humaneval_erp_009=>process_sales_aggregation( ).

    cl_abap_unit_assert=>assert_true( act = lv_success ).

    SELECT * FROM zsales_aggr INTO TABLE @lt_actual_result.

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual_result )
      exp = 3
      msg = 'Should have separate entries for different articles' ).

  ENDMETHOD.

  METHOD test_diff_people_same_article.
    DATA: lt_actual_result TYPE TABLE OF zsales_aggr,
          lv_success       TYPE abap_bool.

    INSERT zsales_positions FROM TABLE @( VALUE #(
      ( zid = 1 zname = 'SMITH' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '1000.00' )
      ( zid = 2 zname = 'JONES' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '800.00' )
      ( zid = 3 zname = 'BROWN' zarticle = 'LAPTOP' zcurrency = 'USD' zrev = '1200.00' )
    ) ).
    COMMIT WORK.

    lv_success = z_humaneval_erp_009=>process_sales_aggregation( ).

    cl_abap_unit_assert=>assert_true( act = lv_success ).

    SELECT * FROM zsales_aggr INTO TABLE @lt_actual_result.

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual_result )
      exp = 3
      msg = 'Should have separate entries for different salespeople' ).

  ENDMETHOD.

ENDCLASS.