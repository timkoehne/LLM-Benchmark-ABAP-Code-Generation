CLASS ltcl_test_flight_helper DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS:
      setup,
      teardown,
      test_basic_flight_retrieval FOR TESTING,
      test_multiple_airlines FOR TESTING,
      test_multi_flights_same FOR TESTING,
      test_no_flights FOR TESTING,
      test_single_flight FOR TESTING,
      test_flight_date_sorting FOR TESTING,
      test_empty_airline_code FOR TESTING.

    DATA: lt_sflight_backup TYPE STANDARD TABLE OF sflight.

ENDCLASS.

CLASS ltcl_test_flight_helper IMPLEMENTATION.

  METHOD setup.
    " Backup existing data
    SELECT * FROM sflight INTO TABLE @lt_sflight_backup.

    " Clear table for clean testing
    DELETE FROM sflight.
  ENDMETHOD.

  METHOD teardown.
    " Restore original data
    DELETE FROM sflight.

    IF lines( lt_sflight_backup ) > 0.
      INSERT sflight FROM TABLE @lt_sflight_backup.
    ENDIF.
  ENDMETHOD.

  METHOD test_basic_flight_retrieval.
    " Test data setup
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                     price = '150.00' currency = 'EUR' seatsmax = 180 seatsocc = 90 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1002' fldate = '20250723'
                     price = '140.00' currency = 'EUR' seatsmax = 160 seatsocc = 80 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'AF' connid = '2001' fldate = '20250722'
                     price = '170.00' currency = 'EUR' seatsmax = 150 seatsocc = 150 ) ).

    " Execute method
    DATA(lt_flights) = z_humaneval_erp_013=>get_flights_for_airline( iv_carrid = 'LH' ).

    " Assertions
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_flights )
      exp = 2
      msg = 'Should return exactly 2 flights for LH'
    ).

    " Check first flight
    READ TABLE lt_flights INTO DATA(ls_flight) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_flight-connid
      exp = '1001'
      msg = 'First flight should be connection 1001'
    ).
    cl_abap_unit_assert=>assert_equals(
      act = ls_flight-fldate
      exp = '20250722'
      msg = 'First flight date should be 20250722'
    ).

    " Check second flight
    READ TABLE lt_flights INTO ls_flight INDEX 2.
    cl_abap_unit_assert=>assert_equals(
      act = ls_flight-connid
      exp = '1002'
      msg = 'Second flight should be connection 1002'
    ).
  ENDMETHOD.

  METHOD test_multiple_airlines.
    " Test with 4 different airlines
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                     price = '150.00' currency = 'EUR' seatsmax = 180 seatsocc = 90 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'AF' connid = '2001' fldate = '20250722'
                     price = '170.00' currency = 'EUR' seatsmax = 150 seatsocc = 150 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'BA' connid = '3001' fldate = '20250722'
                     price = '200.00' currency = 'GBP' seatsmax = 200 seatsocc = 100 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'UA' connid = '4001' fldate = '20250722'
                     price = '180.00' currency = 'USD' seatsmax = 220 seatsocc = 110 ) ).

    " Test each airline separately
    DATA(lt_lh_flights) = z_humaneval_erp_013=>get_flights_for_airline( iv_carrid = 'LH' ).
    DATA(lt_af_flights) = z_humaneval_erp_013=>get_flights_for_airline( iv_carrid = 'AF' ).
    DATA(lt_ba_flights) = z_humaneval_erp_013=>get_flights_for_airline( iv_carrid = 'BA' ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_lh_flights )
      exp = 1
      msg = 'LH should have exactly 1 flight'
    ).
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_af_flights )
      exp = 1
      msg = 'AF should have exactly 1 flight'
    ).
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_ba_flights )
      exp = 1
      msg = 'BA should have exactly 1 flight'
    ).
  ENDMETHOD.

  METHOD test_multi_flights_same.
    " Test multiple flights for same airline
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                     price = '150.00' currency = 'EUR' seatsmax = 180 seatsocc = 90 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1002' fldate = '20250723'
                     price = '140.00' currency = 'EUR' seatsmax = 160 seatsocc = 80 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1003' fldate = '20250724'
                     price = '160.00' currency = 'EUR' seatsmax = 170 seatsocc = 85 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1004' fldate = '20250721'
                     price = '155.00' currency = 'EUR' seatsmax = 175 seatsocc = 88 ) ).

    DATA(lt_flights) = z_humaneval_erp_013=>get_flights_for_airline( iv_carrid = 'LH' ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_flights )
      exp = 4
      msg = 'Should return exactly 4 flights for LH'
    ).

    " Check sorting - first flight should be earliest date
    READ TABLE lt_flights INTO DATA(ls_flight) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_flight-fldate
      exp = '20250721'
      msg = 'First flight should be earliest date (20250721)'
    ).
  ENDMETHOD.

  METHOD test_no_flights.
    " Test airline with no flights
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                     price = '150.00' currency = 'EUR' seatsmax = 180 seatsocc = 90 ) ).

    " Search for different airline
    DATA(lt_flights) = z_humaneval_erp_013=>get_flights_for_airline( iv_carrid = 'AF' ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_flights )
      exp = 0
      msg = 'Should return no results when no flights exist for airline'
    ).
  ENDMETHOD.

  METHOD test_single_flight.
    " Test with single flight
    INSERT sflight FROM @( VALUE #( carrid = 'BA' connid = '3001' fldate = '20250725'
                     price = '250.00' currency = 'GBP' seatsmax = 200 seatsocc = 120 ) ).

    DATA(lt_flights) = z_humaneval_erp_013=>get_flights_for_airline( iv_carrid = 'BA' ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_flights )
      exp = 1
      msg = 'Should return exactly 1 flight'
    ).

    READ TABLE lt_flights INTO DATA(ls_flight) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_flight-connid
      exp = '3001'
      msg = 'Connection should be 3001'
    ).
    cl_abap_unit_assert=>assert_equals(
      act = ls_flight-fldate
      exp = '20250725'
      msg = 'Flight date should match'
    ).
  ENDMETHOD.

  METHOD test_flight_date_sorting.
    " Test sorting by date and connection number
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1003' fldate = '20250724'
                     price = '160.00' currency = 'EUR' seatsmax = 170 seatsocc = 85 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                     price = '150.00' currency = 'EUR' seatsmax = 180 seatsocc = 90 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1002' fldate = '20250722'
                     price = '140.00' currency = 'EUR' seatsmax = 160 seatsocc = 80 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1004' fldate = '20250723'
                     price = '155.00' currency = 'EUR' seatsmax = 175 seatsocc = 88 ) ).

    DATA(lt_flights) = z_humaneval_erp_013=>get_flights_for_airline( iv_carrid = 'LH' ).

    " Check correct sorting order
    READ TABLE lt_flights INTO DATA(ls_flight) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = |{ ls_flight-fldate }{ ls_flight-connid }|
      exp = '202507221001'
      msg = 'First should be earliest date with lowest connection'
    ).

    READ TABLE lt_flights INTO ls_flight INDEX 2.
    cl_abap_unit_assert=>assert_equals(
      act = |{ ls_flight-fldate }{ ls_flight-connid }|
      exp = '202507221002'
      msg = 'Second should be same date with next connection'
    ).
  ENDMETHOD.

  METHOD test_empty_airline_code.
    " Test with empty airline code
    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '1001' fldate = '20250722'
                     price = '150.00' currency = 'EUR' seatsmax = 180 seatsocc = 90 ) ).

    DATA(lt_flights) = z_humaneval_erp_013=>get_flights_for_airline( iv_carrid = '' ).

    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_flights )
      exp = 0
      msg = 'Should return empty table for empty airline code'
    ).
  ENDMETHOD.

ENDCLASS.