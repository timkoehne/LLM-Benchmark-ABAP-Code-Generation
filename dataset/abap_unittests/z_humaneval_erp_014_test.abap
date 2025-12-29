CLASS ltc_booking_counter_test DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS:
      setup,
      teardown,
      test_count_multiple_bookings FOR TESTING,
      test_count_single_booking FOR TESTING,
      test_count_no_bookings FOR TESTING,
      test_count_different_carriers FOR TESTING,
      test_count_different_connids FOR TESTING,
      test_count_different_dates FOR TESTING,
      prepare_test_data.

    DATA: lt_test_data TYPE TABLE OF sbook.
ENDCLASS.

CLASS ltc_booking_counter_test IMPLEMENTATION.
  METHOD setup.
    " Prepare test data for each test
    prepare_test_data( ).
  ENDMETHOD.

  METHOD teardown.
    " Clean up test data
    DELETE FROM sbook WHERE carrid IN ('LH', 'AF', 'BA').
    CLEAR lt_test_data.
  ENDMETHOD.

  METHOD prepare_test_data.
    " Clear any existing test data
    CLEAR lt_test_data.

    " Prepare test data set
    lt_test_data = VALUE #(
      " LH 1001 on 20250722 - 2 bookings
      ( carrid = 'LH' connid = '1001' fldate = '20250722' bookid = 'B001' customid = 'C001' )
      ( carrid = 'LH' connid = '1001' fldate = '20250722' bookid = 'B002' customid = 'C002' )

      " LH 1002 on 20250722 - 1 booking
      ( carrid = 'LH' connid = '1002' fldate = '20250722' bookid = 'B003' customid = 'C003' )

      " AF 2001 on 20250722 - 1 booking
      ( carrid = 'AF' connid = '2001' fldate = '20250722' bookid = 'B004' customid = 'C004' )

      " LH 1001 on 20250723 - 1 booking (different date)
      ( carrid = 'LH' connid = '1001' fldate = '20250723' bookid = 'B005' customid = 'C005' )

      " BA 3001 on 20250722 - 3 bookings
      ( carrid = 'BA' connid = '3001' fldate = '20250722' bookid = 'B006' customid = 'C006' )
      ( carrid = 'BA' connid = '3001' fldate = '20250722' bookid = 'B007' customid = 'C007' )
      ( carrid = 'BA' connid = '3001' fldate = '20250722' bookid = 'B008' customid = 'C008' )
    ).

    " Insert test data
    INSERT sbook FROM TABLE lt_test_data.
  ENDMETHOD.

  METHOD test_count_multiple_bookings.
    " Test counting multiple bookings for the same flight
    DATA(lv_count) = z_humaneval_erp_014=>count_bookings_for_flight(
      iv_carrid = 'LH'
      iv_connid = '1001'
      iv_fldate = '20250722'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = lv_count
      exp = 2
      msg = 'Should return 2 bookings for LH 1001 on 20250722'
    ).
  ENDMETHOD.

  METHOD test_count_single_booking.
    " Test counting a single booking
    DATA(lv_count) = z_humaneval_erp_014=>count_bookings_for_flight(
      iv_carrid = 'LH'
      iv_connid = '1002'
      iv_fldate = '20250722'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = lv_count
      exp = 1
      msg = 'Should return 1 booking for LH 1002 on 20250722'
    ).
  ENDMETHOD.

  METHOD test_count_no_bookings.
    " Test counting when no bookings exist
    DATA(lv_count) = z_humaneval_erp_014=>count_bookings_for_flight(
      iv_carrid = 'XX'
      iv_connid = '9999'
      iv_fldate = '20250722'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = lv_count
      exp = 0
      msg = 'Should return 0 bookings for non-existent flight'
    ).
  ENDMETHOD.

  METHOD test_count_different_carriers.
    " Test that different carriers are distinguished
    DATA(lv_count_lh) = z_humaneval_erp_014=>count_bookings_for_flight(
      iv_carrid = 'LH'
      iv_connid = '1001'
      iv_fldate = '20250722'
    ).

    DATA(lv_count_af) = z_humaneval_erp_014=>count_bookings_for_flight(
      iv_carrid = 'AF'
      iv_connid = '2001'
      iv_fldate = '20250722'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = lv_count_lh
      exp = 2
      msg = 'Should return 2 bookings for LH flight'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = lv_count_af
      exp = 1
      msg = 'Should return 1 booking for AF flight'
    ).
  ENDMETHOD.

  METHOD test_count_different_connids.
    " Test that different connection IDs are distinguished
    DATA(lv_count_1001) = z_humaneval_erp_014=>count_bookings_for_flight(
      iv_carrid = 'LH'
      iv_connid = '1001'
      iv_fldate = '20250722'
    ).

    DATA(lv_count_1002) = z_humaneval_erp_014=>count_bookings_for_flight(
      iv_carrid = 'LH'
      iv_connid = '1002'
      iv_fldate = '20250722'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = lv_count_1001
      exp = 2
      msg = 'Should return 2 bookings for connection 1001'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = lv_count_1002
      exp = 1
      msg = 'Should return 1 booking for connection 1002'
    ).
  ENDMETHOD.

  METHOD test_count_different_dates.
    " Test that different dates are distinguished
    DATA(lv_count_0722) = z_humaneval_erp_014=>count_bookings_for_flight(
      iv_carrid = 'LH'
      iv_connid = '1001'
      iv_fldate = '20250722'
    ).

    DATA(lv_count_0723) = z_humaneval_erp_014=>count_bookings_for_flight(
      iv_carrid = 'LH'
      iv_connid = '1001'
      iv_fldate = '20250723'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = lv_count_0722
      exp = 2
      msg = 'Should return 2 bookings for 20250722'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = lv_count_0723
      exp = 1
      msg = 'Should return 1 booking for 20250723'
    ).
  ENDMETHOD.
ENDCLASS.