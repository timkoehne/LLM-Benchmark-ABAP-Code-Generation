CLASS z_humaneval_erp_014 DEFINITION FINAL PUBLIC.
  PUBLIC SECTION.
    CLASS-METHODS: count_bookings_for_flight
      IMPORTING
        iv_carrid       TYPE char3
        iv_connid       TYPE numc4
        iv_fldate       TYPE dats
      RETURNING
        VALUE(rv_count) TYPE i.
ENDCLASS.

CLASS z_humaneval_erp_014 IMPLEMENTATION.
  METHOD count_bookings_for_flight.
    " Initialize counter
    rv_count = 0.

    " Count bookings matching the flight criteria
    SELECT COUNT( * )
      FROM sbook
      INTO rv_count
      WHERE carrid = iv_carrid
        AND connid = iv_connid
        AND fldate = iv_fldate.
  ENDMETHOD.
ENDCLASS.