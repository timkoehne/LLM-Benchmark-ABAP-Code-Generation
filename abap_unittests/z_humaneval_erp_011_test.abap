CLASS ltcl_test_flight_search DEFINITION
  FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    TYPES: BEGIN OF ty_flight_result,
             airline_name     TYPE char40,
             departure_city   TYPE char20,
             destination_city TYPE char20,
             flight_time      TYPE i,
             available_seats  TYPE i,
           END OF ty_flight_result.

    TYPES: tt_flight_results TYPE STANDARD TABLE OF ty_flight_result.


    METHODS: setup,
      teardown,
      test_get_flights_normal FOR TESTING,
      test_get_flights_no_results FOR TESTING,
      test_get_flights_invalid_date FOR TESTING,
      test_get_flights_empty_city FOR TESTING,
      test_method_valid_params FOR TESTING,
      test_method_no_seats FOR TESTING,
      test_method_future_date FOR TESTING.

    DATA: lt_scarr_backup   TYPE STANDARD TABLE OF scarr,
          lt_spfli_backup   TYPE STANDARD TABLE OF spfli,
          lt_sflight_backup TYPE STANDARD TABLE OF sflight,
          lt_actual         TYPE STANDARD TABLE OF ty_flight_result.


ENDCLASS.

CLASS ltcl_test_flight_search IMPLEMENTATION.

  METHOD setup.
    " Backup existing data
    SELECT * FROM scarr INTO TABLE @lt_scarr_backup.
    SELECT * FROM spfli INTO TABLE @lt_spfli_backup.
    SELECT * FROM sflight INTO TABLE @lt_sflight_backup.

    " Clear tables for clean testing
    DELETE FROM sflight.
    DELETE FROM spfli.
    DELETE FROM scarr.

    " Insert test data
    INSERT scarr FROM @( VALUE #( carrid = 'LH' carrname = 'Lufthansa' ) ).
    INSERT scarr FROM @( VALUE #( carrid = 'AF' carrname = 'Air France' ) ).
    INSERT scarr FROM @( VALUE #( carrid = 'BA' carrname = 'British Airways' ) ).

    INSERT spfli FROM @( VALUE #( carrid = 'LH' connid = '0400'
                                  cityfrom = 'FRANKFURT' cityto = 'NEW YORK'
                                  fltime = 480 ) ).
    INSERT spfli FROM @( VALUE #( carrid = 'AF' connid = '0100'
                                  cityfrom = 'PARIS' cityto = 'LONDON'
                                  fltime = 120 ) ).
    INSERT spfli FROM @( VALUE #( carrid = 'BA' connid = '0200'
                                  cityfrom = 'LONDON' cityto = 'BERLIN'
                                  fltime = 180 ) ).

    INSERT sflight FROM @( VALUE #( carrid = 'LH' connid = '0400'
                                    fldate = '20241201' seatsmax = 300
                                    seatsocc = 250 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'AF' connid = '0100'
                                    fldate = '20241201' seatsmax = 200
                                    seatsocc = 180 ) ).
    INSERT sflight FROM @( VALUE #( carrid = 'BA' connid = '0200'
                                    fldate = '20241201' seatsmax = 150
                                    seatsocc = 150 ) ). " Fully booked

    CLEAR lt_actual.
  ENDMETHOD.

  METHOD teardown.
    " Restore original data
    DELETE FROM sflight.
    DELETE FROM spfli.
    DELETE FROM scarr.

    IF lines( lt_scarr_backup ) > 0.
      INSERT scarr FROM TABLE @lt_scarr_backup.
    ENDIF.

    IF lines( lt_spfli_backup ) > 0.
      INSERT spfli FROM TABLE @lt_spfli_backup.
    ENDIF.

    IF lines( lt_sflight_backup ) > 0.
      INSERT sflight FROM TABLE @lt_sflight_backup.
    ENDIF.
  ENDMETHOD.

  METHOD test_get_flights_normal.
    " Test: Normale Flugsuche mit verfügbaren Plätzen
    lt_actual = z_humaneval_erp_011=>get_available_flights(
      origin_city = 'FRANKFURT'
      destination_city = 'NEW YORK'
      flight_date = '20241201'
    ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 1
      msg = 'Should find exactly 1 flight'
    ).

    READ TABLE lt_actual INTO DATA(ls_flight) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_flight-airline_name
      exp = 'Lufthansa'
      msg = 'Airline name should be Lufthansa'
    ).

    cl_abap_unit_assert=>assert_equals(
      act = ls_flight-available_seats
      exp = 50
      msg = 'Available seats should be 50 (300-250)'
    ).
  ENDMETHOD.

  METHOD test_get_flights_no_results.
    " Test: Suche nach nicht existierender Route
    lt_actual = z_humaneval_erp_011=>get_available_flights(
      origin_city = 'MUNICH'
      destination_city = 'TOKYO'
      flight_date = '20241201'
    ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 0
      msg = 'Should find no flights for non-existing route'
    ).
  ENDMETHOD.

  METHOD test_get_flights_invalid_date.
    " Test: Suche mit vergangenem Datum
    lt_actual = z_humaneval_erp_011=>get_available_flights(
      origin_city = 'FRANKFURT'
      destination_city = 'NEW YORK'
      flight_date = '19801201'
    ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 0
      msg = 'Should find no flights for past date'
    ).
  ENDMETHOD.

  METHOD test_get_flights_empty_city.
    " Test: Suche mit leerem Parameter
    lt_actual = z_humaneval_erp_011=>get_available_flights(
      origin_city = ''
      destination_city = 'NEW YORK'
      flight_date = '20241201'
    ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 0
      msg = 'Should find no flights with empty origin city'
    ).
  ENDMETHOD.

  METHOD test_method_valid_params.
    " Test: Methodenausführung funktioniert korrekt
    lt_actual = z_humaneval_erp_011=>get_available_flights(
      origin_city = 'PARIS'
      destination_city = 'LONDON'
      flight_date = '20241201'
    ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 1
      msg = 'Should find Air France flight'
    ).

    READ TABLE lt_actual INTO DATA(ls_flight) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_flight-flight_time
      exp = 120
      msg = 'Flight time should be 120 minutes'
    ).
  ENDMETHOD.

  METHOD test_method_no_seats.
    " Test: Flug ohne verfügbare Plätze wird nicht angezeigt
    lt_actual = z_humaneval_erp_011=>get_available_flights(
      origin_city = 'LONDON'
      destination_city = 'BERLIN'
      flight_date = '20241201'
    ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 0
      msg = 'Should find no flights when fully booked'
    ).
  ENDMETHOD.

  METHOD test_method_future_date.
    " Test: Suche mit zukünftigem nicht vorhandenem Datum
    lt_actual = z_humaneval_erp_011=>get_available_flights(
      origin_city = 'FRANKFURT'
      destination_city = 'NEW YORK'
      flight_date = '20251201'
    ).

    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 0
      msg = 'Should find no flights for future date not in data'
    ).
  ENDMETHOD.

ENDCLASS.