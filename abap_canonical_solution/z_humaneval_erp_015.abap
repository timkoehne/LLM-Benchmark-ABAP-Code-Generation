CLASS z_humaneval_erp_015 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.
    TYPES: BEGIN OF ty_route_revenue,
             cityfrom TYPE c LENGTH 20,
             cityto   TYPE c LENGTH 20,
             revenue  TYPE p LENGTH 8 DECIMALS 2,
           END OF ty_route_revenue.

    TYPES: tt_route_revenue TYPE TABLE OF ty_route_revenue WITH EMPTY KEY.

    CLASS-METHODS: get_route_profitability
      RETURNING VALUE(rt_route_revenue) TYPE z_humaneval_erp_015=>tt_route_revenue.

  PRIVATE SECTION.
ENDCLASS.

CLASS z_humaneval_erp_015 IMPLEMENTATION.
  METHOD get_route_profitability.
    DATA: lt_flight_data TYPE TABLE OF sflight,
          lt_route_data  TYPE TABLE OF spfli,
          lt_combined    TYPE TABLE OF ty_route_revenue,
          ls_route       TYPE ty_route_revenue.

    " Get all flight data
    SELECT carrid, connid, fldate, price, seatsocc
      FROM sflight
      INTO TABLE @DATA(lt_flights).

    " Get all route data
    SELECT carrid, connid, cityfrom, cityto
      FROM spfli
      INTO TABLE @DATA(lt_routes).

    " Calculate revenue for each flight and group by route
    LOOP AT lt_flights INTO DATA(ls_flight).
      " Find corresponding route information
      READ TABLE lt_routes INTO DATA(ls_route_info)
        WITH KEY carrid = ls_flight-carrid
                 connid = ls_flight-connid.

      IF sy-subrc = 0.
        " Calculate revenue for this flight (price * occupied seats)
        DATA: lv_flight_revenue TYPE p LENGTH 8 DECIMALS 2.
        lv_flight_revenue = ls_flight-price * ls_flight-seatsocc.

        " Check if route already exists in result table
        READ TABLE lt_combined INTO ls_route
          WITH KEY cityfrom = ls_route_info-cityfrom
                   cityto   = ls_route_info-cityto.

        IF sy-subrc = 0.
          " Route exists, add to existing revenue
          ls_route-revenue = ls_route-revenue + lv_flight_revenue.
          MODIFY lt_combined FROM ls_route
            TRANSPORTING revenue
            WHERE cityfrom = ls_route_info-cityfrom
              AND cityto   = ls_route_info-cityto.
        ELSE.
          " New route, create entry
          CLEAR ls_route.
          ls_route-cityfrom = ls_route_info-cityfrom.
          ls_route-cityto   = ls_route_info-cityto.
          ls_route-revenue  = lv_flight_revenue.
          APPEND ls_route TO lt_combined.
        ENDIF.
      ENDIF.
    ENDLOOP.

    " Sort by revenue in descending order
    SORT lt_combined BY revenue DESCENDING.

    rt_route_revenue = lt_combined.
  ENDMETHOD.
ENDCLASS.