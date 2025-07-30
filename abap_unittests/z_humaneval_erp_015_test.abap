CLASS ltcl_test_route_profitability DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS:
      setup,
      teardown,
      test_basic_route_calc FOR TESTING,
      test_multi_flights_same_route FOR TESTING,
      test_multiple_routes FOR TESTING,
      test_no_flight_data FOR TESTING,
      test_no_route_data FOR TESTING,
      test_orphaned_flights FOR TESTING,
      test_zero_revenue_flights FOR TESTING,
      test_sorting_by_revenue FOR TESTING,
      test_large_numbers FOR TESTING.

    DATA: mo_cut TYPE REF TO z_humaneval_erp_015.

ENDCLASS.

CLASS ltcl_test_route_profitability IMPLEMENTATION.

  METHOD setup.
    " Create instance of class under test
    CREATE OBJECT mo_cut.

    " Clear all data from tables to ensure clean test environment
    DELETE FROM sflight.
    DELETE FROM spfli.
  ENDMETHOD.

  METHOD teardown.
    " Clean up all test data
    DELETE FROM sflight.
    DELETE FROM spfli.
    CLEAR mo_cut.
  ENDMETHOD.

  METHOD test_basic_route_calc.
    " Test basic revenue calculation for a single route

    " Prepare test data
    DATA: lt_flight_data TYPE TABLE OF sflight,
          lt_route_data TYPE TABLE OF spfli,
          ls_flight TYPE sflight,
          ls_route TYPE spfli.

    " Create route data
    ls_route-carrid = 'TST'.
    ls_route-connid = '0001'.
    ls_route-cityfrom = 'Frankfurt'.
    ls_route-cityto = 'New York'.
    APPEND ls_route TO lt_route_data.

    " Create flight data
    ls_flight-carrid = 'TST'.
    ls_flight-connid = '0001'.
    ls_flight-fldate = '20241201'.
    ls_flight-price = '300.00'.
    ls_flight-seatsocc = 50.
    APPEND ls_flight TO lt_flight_data.

    " Insert test data
    INSERT spfli FROM TABLE lt_route_data.
    INSERT sflight FROM TABLE lt_flight_data.

    " Execute method
    DATA(lt_actual) = z_humaneval_erp_015=>get_route_profitability( ).

    " Verify results
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 1
      msg = 'Should return exactly one route' ).

    READ TABLE lt_actual INTO DATA(ls_actual) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-cityfrom
      exp = 'Frankfurt'
      msg = 'City from should match' ).

    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-cityto
      exp = 'New York'
      msg = 'City to should match' ).

    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-revenue
      exp = '15000.00'
      msg = 'Revenue should be 300 * 50 = 15000' ).
  ENDMETHOD.

  METHOD test_multi_flights_same_route.
    " Test that multiple flights on the same route are aggregated

    DATA: lt_flight_data TYPE TABLE OF sflight,
          lt_route_data TYPE TABLE OF spfli,
          ls_flight TYPE sflight,
          ls_route TYPE spfli.

    " Create route data
    ls_route-carrid = 'TST'.
    ls_route-connid = '0001'.
    ls_route-cityfrom = 'Frankfurt'.
    ls_route-cityto = 'New York'.
    APPEND ls_route TO lt_route_data.

    " Create first flight
    ls_flight-carrid = 'TST'.
    ls_flight-connid = '0001'.
    ls_flight-fldate = '20241201'.
    ls_flight-price = '300.00'.
    ls_flight-seatsocc = 50.
    APPEND ls_flight TO lt_flight_data.

    " Create second flight same route
    ls_flight-fldate = '20241202'.
    ls_flight-price = '250.00'.
    ls_flight-seatsocc = 40.
    APPEND ls_flight TO lt_flight_data.

    " Insert test data
    INSERT spfli FROM TABLE lt_route_data.
    INSERT sflight FROM TABLE lt_flight_data.

    " Execute method
    DATA(lt_actual) = z_humaneval_erp_015=>get_route_profitability( ).

    " Verify aggregation
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 1
      msg = 'Should return one aggregated route' ).

    READ TABLE lt_actual INTO DATA(ls_actual) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-revenue
      exp = '25000.00'
      msg = 'Revenue should be (300*50) + (250*40) = 25000' ).
  ENDMETHOD.

  METHOD test_multiple_routes.
    " Test multiple different routes with proper sorting

    DATA: lt_flight_data TYPE TABLE OF sflight,
          lt_route_data TYPE TABLE OF spfli,
          ls_flight TYPE sflight,
          ls_route TYPE spfli.

    " Route 1: Frankfurt -> Tokyo
    ls_route-carrid = 'TST'.
    ls_route-connid = '0001'.
    ls_route-cityfrom = 'Frankfurt'.
    ls_route-cityto = 'Tokyo'.
    APPEND ls_route TO lt_route_data.

    " Route 2: Berlin -> London
    ls_route-connid = '0002'.
    ls_route-cityfrom = 'Berlin'.
    ls_route-cityto = 'London'.
    APPEND ls_route TO lt_route_data.

    " Route 3: Munich -> Paris
    ls_route-connid = '0003'.
    ls_route-cityfrom = 'Munich'.
    ls_route-cityto = 'Paris'.
    APPEND ls_route TO lt_route_data.

    " Flight 1: Frankfurt -> Tokyo (highest revenue)
    ls_flight-carrid = 'TST'.
    ls_flight-connid = '0001'.
    ls_flight-fldate = '20241201'.
    ls_flight-price = '600.00'.
    ls_flight-seatsocc = 50.
    APPEND ls_flight TO lt_flight_data.

    " Flight 2: Berlin -> London (medium revenue)
    ls_flight-connid = '0002'.
    ls_flight-price = '400.00'.
    ls_flight-seatsocc = 50.
    APPEND ls_flight TO lt_flight_data.

    " Flight 3: Munich -> Paris (lowest revenue)
    ls_flight-connid = '0003'.
    ls_flight-price = '200.00'.
    ls_flight-seatsocc = 50.
    APPEND ls_flight TO lt_flight_data.

    " Insert test data
    INSERT spfli FROM TABLE lt_route_data.
    INSERT sflight FROM TABLE lt_flight_data.

    " Execute method
    DATA(lt_actual) = z_humaneval_erp_015=>get_route_profitability( ).

    " Verify results
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 3
      msg = 'Should return three routes' ).

    " Verify sorting (descending by revenue)
    READ TABLE lt_actual INTO DATA(ls_actual) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-cityto
      exp = 'Tokyo'
      msg = 'First route should be highest revenue (Tokyo)' ).
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-revenue
      exp = '30000.00'
      msg = 'Tokyo route revenue should be 30000' ).

    READ TABLE lt_actual INTO ls_actual INDEX 2.
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-cityto
      exp = 'London'
      msg = 'Second route should be London' ).

    READ TABLE lt_actual INTO ls_actual INDEX 3.
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-cityto
      exp = 'Paris'
      msg = 'Third route should be lowest revenue (Paris)' ).
  ENDMETHOD.

  METHOD test_no_flight_data.
    " Test behavior when no flight data exists

    DATA: lt_route_data TYPE TABLE OF spfli,
          ls_route TYPE spfli.

    " Create route data but no flight data
    ls_route-carrid = 'TST'.
    ls_route-connid = '0001'.
    ls_route-cityfrom = 'Frankfurt'.
    ls_route-cityto = 'New York'.
    APPEND ls_route TO lt_route_data.

    INSERT spfli FROM TABLE lt_route_data.

    " Execute method
    DATA(lt_actual) = z_humaneval_erp_015=>get_route_profitability( ).

    " Verify empty result
    cl_abap_unit_assert=>assert_initial(
      act = lt_actual
      msg = 'Should return empty table when no flight data exists' ).
  ENDMETHOD.

  METHOD test_no_route_data.
    " Test behavior when no route data exists

    DATA: lt_flight_data TYPE TABLE OF sflight,
          ls_flight TYPE sflight.

    " Create flight data but no route data
    ls_flight-carrid = 'TST'.
    ls_flight-connid = '0001'.
    ls_flight-fldate = '20241201'.
    ls_flight-price = '300.00'.
    ls_flight-seatsocc = 50.
    APPEND ls_flight TO lt_flight_data.

    INSERT sflight FROM TABLE lt_flight_data.

    " Execute method
    DATA(lt_actual) = z_humaneval_erp_015=>get_route_profitability( ).

    " Should return empty as flights without routes are ignored
    cl_abap_unit_assert=>assert_initial(
      act = lt_actual
      msg = 'Should return empty table when no route data matches' ).
  ENDMETHOD.

  METHOD test_orphaned_flights.
    " Test flights that don't have corresponding route information

    DATA: lt_flight_data TYPE TABLE OF sflight,
          lt_route_data TYPE TABLE OF spfli,
          ls_flight TYPE sflight,
          ls_route TYPE spfli.

    " Create route for connection 0001 only
    ls_route-carrid = 'TST'.
    ls_route-connid = '0001'.
    ls_route-cityfrom = 'Frankfurt'.
    ls_route-cityto = 'New York'.
    APPEND ls_route TO lt_route_data.

    " Flight with matching route
    ls_flight-carrid = 'TST'.
    ls_flight-connid = '0001'.
    ls_flight-fldate = '20241201'.
    ls_flight-price = '300.00'.
    ls_flight-seatsocc = 50.
    APPEND ls_flight TO lt_flight_data.

    " Orphaned flight (no matching route)
    ls_flight-connid = '0002'. " No route exists for 0002
    ls_flight-price = '500.00'.
    ls_flight-seatsocc = 60.
    APPEND ls_flight TO lt_flight_data.

    " Insert test data
    INSERT spfli FROM TABLE lt_route_data.
    INSERT sflight FROM TABLE lt_flight_data.

    " Execute method
    DATA(lt_actual) = z_humaneval_erp_015=>get_route_profitability( ).

    " Should only return the matched flight/route
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 1
      msg = 'Should return only matched flight/route pairs' ).

    READ TABLE lt_actual INTO DATA(ls_actual) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-revenue
      exp = '15000.00'
      msg = 'Should only include revenue from matched flight' ).
  ENDMETHOD.

  METHOD test_zero_revenue_flights.
    " Test flights with zero price or zero occupied seats

    DATA: lt_flight_data TYPE TABLE OF sflight,
          lt_route_data TYPE TABLE OF spfli,
          ls_flight TYPE sflight,
          ls_route TYPE spfli.

    " Route 1
    ls_route-carrid = 'TST'.
    ls_route-connid = '0001'.
    ls_route-cityfrom = 'Frankfurt'.
    ls_route-cityto = 'London'.
    APPEND ls_route TO lt_route_data.

    " Route 2
    ls_route-connid = '0002'.
    ls_route-cityfrom = 'Berlin'.
    ls_route-cityto = 'Munich'.
    APPEND ls_route TO lt_route_data.

    " Flight with zero price
    ls_flight-carrid = 'TST'.
    ls_flight-connid = '0001'.
    ls_flight-fldate = '20241201'.
    ls_flight-price = '0.00'.
    ls_flight-seatsocc = 50.
    APPEND ls_flight TO lt_flight_data.

    " Flight with zero seats
    ls_flight-connid = '0001'.
    ls_flight-fldate = '20241202'.
    ls_flight-price = '300.00'.
    ls_flight-seatsocc = 0.
    APPEND ls_flight TO lt_flight_data.

    " Flight with normal values
    ls_flight-connid = '0002'.
    ls_flight-price = '200.00'.
    ls_flight-seatsocc = 25.
    APPEND ls_flight TO lt_flight_data.

    " Insert test data
    INSERT spfli FROM TABLE lt_route_data.
    INSERT sflight FROM TABLE lt_flight_data.

    " Execute method
    DATA(lt_actual) = z_humaneval_erp_015=>get_route_profitability( ).

    " Should return both routes
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 2
      msg = 'Should return both routes' ).

    " Verify Berlin-Munich has higher revenue and comes first
    READ TABLE lt_actual INTO DATA(ls_actual) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-cityfrom
      exp = 'Berlin'
      msg = 'Berlin route should be first (higher revenue)' ).
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-revenue
      exp = '5000.00'
      msg = 'Berlin route revenue should be 5000' ).

    " Verify Frankfurt-London has zero revenue and comes second
    READ TABLE lt_actual INTO ls_actual INDEX 2.
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-cityfrom
      exp = 'Frankfurt'
      msg = 'Frankfurt route should be second (zero revenue)' ).
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-revenue
      exp = '0.00'
      msg = 'Frankfurt route should have zero revenue' ).
  ENDMETHOD.

  METHOD test_sorting_by_revenue.
    " Test that routes are sorted by revenue in descending order

    DATA: lt_flight_data TYPE TABLE OF sflight,
          lt_route_data TYPE TABLE OF spfli,
          ls_flight TYPE sflight,
          ls_route TYPE spfli.

    " Create 4 routes with different revenues
    " Route revenues will be: 40000, 30000, 20000, 10000

    DO 4 TIMES.
      ls_route-carrid = 'TST'.
      ls_route-connid = |000{ sy-index }|.
      ls_route-cityfrom = |City{ sy-index }From|.
      ls_route-cityto = |City{ sy-index }To|.
      APPEND ls_route TO lt_route_data.

      " Create flights with decreasing revenues
      ls_flight-carrid = 'TST'.
      ls_flight-connid = |000{ sy-index }|.
      ls_flight-fldate = '20241201'.
      ls_flight-price = ( 5 - sy-index ) * 200.  " 800, 600, 400, 200
      ls_flight-seatsocc = 50.
      APPEND ls_flight TO lt_flight_data.
    ENDDO.

    " Insert test data
    INSERT spfli FROM TABLE lt_route_data.
    INSERT sflight FROM TABLE lt_flight_data.

    " Execute method
    DATA(lt_actual) = z_humaneval_erp_015=>get_route_profitability( ).

    " Verify sorting
    DATA: lv_previous_revenue TYPE p LENGTH 8 DECIMALS 2 VALUE '999999.99'.

    LOOP AT lt_actual INTO DATA(ls_route_result).
      cl_abap_unit_assert=>assert_true(
        act = COND #( WHEN ls_route_result-revenue <= lv_previous_revenue THEN abap_true ELSE abap_false )
        msg = |Routes should be sorted descending at position { sy-tabix }| ).
      lv_previous_revenue = ls_route_result-revenue.
    ENDLOOP.

    " Verify specific values
    READ TABLE lt_actual INTO DATA(ls_first) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_first-revenue
      exp = '40000.00'
      msg = 'First route should have highest revenue' ).

    READ TABLE lt_actual INTO DATA(ls_last) INDEX 4.
    cl_abap_unit_assert=>assert_equals(
      act = ls_last-revenue
      exp = '10000.00'
      msg = 'Last route should have lowest revenue' ).
  ENDMETHOD.

  METHOD test_large_numbers.
    " Test with large price and seat numbers

    DATA: lt_flight_data TYPE TABLE OF sflight,
          lt_route_data TYPE TABLE OF spfli,
          ls_flight TYPE sflight,
          ls_route TYPE spfli.

    " Create route
    ls_route-carrid = 'TST'.
    ls_route-connid = '0001'.
    ls_route-cityfrom = 'Frankfurt'.
    ls_route-cityto = 'Tokyo'.
    APPEND ls_route TO lt_route_data.

    " Create flight with large numbers
    ls_flight-carrid = 'TST'.
    ls_flight-connid = '0001'.
    ls_flight-fldate = '20241201'.
    ls_flight-price = '9999.99'.
    ls_flight-seatsocc = 999.
    APPEND ls_flight TO lt_flight_data.

    " Insert test data
    INSERT spfli FROM TABLE lt_route_data.
    INSERT sflight FROM TABLE lt_flight_data.

    " Execute method
    DATA(lt_actual) = z_humaneval_erp_015=>get_route_profitability( ).

    " Verify large number handling
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_actual )
      exp = 1
      msg = 'Should handle large numbers' ).

    READ TABLE lt_actual INTO DATA(ls_actual) INDEX 1.
    cl_abap_unit_assert=>assert_equals(
      act = ls_actual-revenue
      exp = '9989990.01'
      msg = 'Should calculate large revenue correctly' ).
  ENDMETHOD.

ENDCLASS.