CLASS ltcl_test_airline_revenue DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    TYPES: BEGIN OF ty_airline_revenue,
             carrname      TYPE scarr-carrname,
             total_revenue TYPE sbook-forcuram,
           END OF ty_airline_revenue,
           tt_airline_revenue TYPE TABLE OF ty_airline_revenue WITH EMPTY KEY.

    METHODS:
      setup,
      teardown,
      test_basic_revenue_calc FOR TESTING,
      test_multiple_airlines FOR TESTING,
      test_multi_bookings_same FOR TESTING,
      test_no_bookings FOR TESTING,
      test_single_booking FOR TESTING,
      test_different_amounts FOR TESTING.

    DATA: lt_scarr_backup TYPE STANDARD TABLE OF scarr,
          lt_sbook_backup TYPE STANDARD TABLE OF sbook.

ENDCLASS.

CLASS ltcl_test_airline_revenue IMPLEMENTATION.

  METHOD setup.
    " Backup existing data
    SELECT * FROM scarr INTO TABLE @lt_scarr_backup.
    SELECT * FROM sbook INTO TABLE @lt_sbook_backup.

    " Clear tables for clean testing
    DELETE FROM sbook.
    DELETE FROM scarr.
  ENDMETHOD.

  METHOD teardown.
    " Restore original data
    DELETE FROM sbook.
    DELETE FROM scarr.

    IF lines( lt_scarr_backup ) > 0.
      INSERT scarr FROM TABLE @lt_scarr_backup.
    ENDIF.

    IF lines( lt_sbook_backup ) > 0.
      INSERT sbook FROM TABLE @lt_sbook_backup.
    ENDIF.
  ENDMETHOD.

  METHOD test_basic_revenue_calc.
    " Test data setup
    INSERT scarr FROM @( VALUE #( carrid = 'LH' carrname = 'Lufthansa' ) ).
    INSERT scarr FROM @( VALUE #( carrid = 'AF' carrname = 'Air France' ) ).

    INSERT sbook FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                   bookid = 'B001' forcuram = '150.00' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'LH' connid = '1002' fldate = '20250723'
                   bookid = 'B002' forcuram = '120.00' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'AF' connid = '2001' fldate = '20250722'
                   bookid = 'B003' forcuram = '200.00' ) ).

    " Execute method - FIXED: Using RETURNING parameter
    DATA: lt_result TYPE tt_airline_revenue.
    lt_result = z_humaneval_erp_012=>get_total_revenue_by_airline( ).

    " Assertions
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 2
      msg = 'Should return exactly 2 airlines'
    ).

    " Check Lufthansa total
    READ TABLE lt_result INTO DATA(ls_result) WITH KEY carrname = 'Lufthansa'.
    cl_abap_unit_assert=>assert_equals(
      act = ls_result-total_revenue
      exp = '270.00'
      msg = 'Lufthansa total revenue should be 270.00'
    ).

    " Check Air France total
    READ TABLE lt_result INTO ls_result WITH KEY carrname = 'Air France'.
    cl_abap_unit_assert=>assert_equals(
      act = ls_result-total_revenue
      exp = '200.00'
      msg = 'Air France total revenue should be 200.00'
    ).
  ENDMETHOD.

  METHOD test_multiple_airlines.
    " Test with 4 different airlines
    INSERT scarr FROM @( VALUE #( carrid = 'LH' carrname = 'Lufthansa' ) ).
    INSERT scarr FROM @( VALUE #( carrid = 'AF' carrname = 'Air France' ) ).
    INSERT scarr FROM @( VALUE #( carrid = 'BA' carrname = 'British Airways' ) ).
    INSERT scarr FROM @( VALUE #( carrid = 'UA' carrname = 'United Airlines' ) ).

    INSERT sbook FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                   bookid = 'B001' forcuram = '100.00' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'AF' connid = '2001' fldate = '20250722'
                   bookid = 'B002' forcuram = '150.00' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'BA' connid = '3001' fldate = '20250722'
                   bookid = 'B003' forcuram = '300.00' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'UA' connid = '4001' fldate = '20250722'
                   bookid = 'B004' forcuram = '250.00' ) ).

    " Execute method - FIXED: Using RETURNING parameter
    DATA: lt_result TYPE tt_airline_revenue.
    lt_result = z_humaneval_erp_012=>get_total_revenue_by_airline( ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 4
      msg = 'Should return exactly 4 airlines'
    ).
  ENDMETHOD.

  METHOD test_multi_bookings_same.
    " Test multiple bookings for same airline
    INSERT scarr FROM @( VALUE #( carrid = 'LH' carrname = 'Lufthansa' ) ).

    INSERT sbook FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                   bookid = 'B001' forcuram = '100.00' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                   bookid = 'B002' forcuram = '150.00' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'LH' connid = '1002' fldate = '20250723'
                   bookid = 'B003' forcuram = '200.00' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'LH' connid = '1003' fldate = '20250724'
                   bookid = 'B004' forcuram = '75.50' ) ).

    " Execute method - FIXED: Using RETURNING parameter
    DATA: lt_result TYPE tt_airline_revenue.
    lt_result = z_humaneval_erp_012=>get_total_revenue_by_airline( ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 1
      msg = 'Should return exactly 1 airline'
    ).

    READ TABLE lt_result INTO DATA(ls_result) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_result-total_revenue
      exp = '525.50'
      msg = 'Total revenue should be sum of all bookings: 525.50'
    ).
  ENDMETHOD.

  METHOD test_no_bookings.
    " Test airlines with no bookings
    INSERT scarr FROM @( VALUE #( carrid = 'LH' carrname = 'Lufthansa' ) ).
    INSERT scarr FROM @( VALUE #( carrid = 'AF' carrname = 'Air France' ) ).

    " No bookings inserted

    " Execute method - FIXED: Using RETURNING parameter
    DATA: lt_result TYPE tt_airline_revenue.
    lt_result = z_humaneval_erp_012=>get_total_revenue_by_airline( ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 0
      msg = 'Should return no results when no bookings exist'
    ).
  ENDMETHOD.

  METHOD test_single_booking.
    " Test with single booking
    INSERT scarr FROM @( VALUE #( carrid = 'BA' carrname = 'British Airways' ) ).

    INSERT sbook FROM @( VALUE #( carrid = 'BA' connid = '3001' fldate = '20250722'
                   bookid = 'B001' forcuram = '450.75' ) ).

    " Execute method - FIXED: Using RETURNING parameter
    DATA: lt_result TYPE tt_airline_revenue.
    lt_result = z_humaneval_erp_012=>get_total_revenue_by_airline( ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 1
      msg = 'Should return exactly 1 airline'
    ).

    READ TABLE lt_result INTO DATA(ls_result) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_result-carrname
      exp = 'British Airways'
      msg = 'Airline name should be British Airways'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = ls_result-total_revenue
      exp = '450.75'
      msg = 'Total revenue should match single booking amount'
    ).
  ENDMETHOD.

  METHOD test_different_amounts.
    " Test with various booking amounts including decimals
    INSERT scarr FROM @( VALUE #( carrid = 'LH' carrname = 'Lufthansa' ) ).
    INSERT scarr FROM @( VALUE #( carrid = 'AF' carrname = 'Air France' ) ).

    INSERT sbook FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                   bookid = 'B001' forcuram = '99.99' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'LH' connid = '1002' fldate = '20250723'
                   bookid = 'B002' forcuram = '0.01' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'AF' connid = '2001' fldate = '20250722'
                   bookid = 'B003' forcuram = '1000.00' ) ).
    INSERT sbook FROM @( VALUE #( carrid = 'AF' connid = '2002' fldate = '20250723'
                   bookid = 'B004' forcuram = '0.50' ) ).

    " Execute method - FIXED: Using RETURNING parameter
    DATA: lt_result TYPE tt_airline_revenue.
    lt_result = z_humaneval_erp_012=>get_total_revenue_by_airline( ).

    " Check Lufthansa total (99.99 + 0.01 = 100.00)
    READ TABLE lt_result INTO DATA(ls_result) WITH KEY carrname = 'Lufthansa'.
    cl_abap_unit_assert=>assert_equals(
      act = ls_result-total_revenue
      exp = '100.00'
      msg = 'Lufthansa total should handle decimal precision correctly'
    ).

    " Check Air France total (1000.00 + 0.50 = 1000.50)
    READ TABLE lt_result INTO ls_result WITH KEY carrname = 'Air France'.
    cl_abap_unit_assert=>assert_equals(
      act = ls_result-total_revenue
      exp = '1000.50'
      msg = 'Air France total should handle decimal precision correctly'
    ).
  ENDMETHOD.

ENDCLASS.