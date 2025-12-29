CLASS z_humaneval_erp_013 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.

    " Types for return values
    TYPES: BEGIN OF ty_flight_result,
             connid TYPE sflight-connid,
             fldate TYPE sflight-fldate,
           END OF ty_flight_result.

    TYPES: tt_flight_results TYPE TABLE OF ty_flight_result WITH EMPTY KEY.

    " Static method for querying flights of an airline
    CLASS-METHODS: get_flights_for_airline
      IMPORTING
        iv_carrid         TYPE sflight-carrid
      RETURNING
        VALUE(et_flights) TYPE tt_flight_results
      RAISING
        cx_sy_open_sql_db.

  PROTECTED SECTION.
  PRIVATE SECTION.

ENDCLASS.


CLASS z_humaneval_erp_013 IMPLEMENTATION.

  METHOD get_flights_for_airline.

    " Initialize the export table
    CLEAR et_flights.

    " Input validation
    IF iv_carrid IS INITIAL.
      " Return an empty table if airline code is missing
      RETURN.
    ENDIF.

    " Database query for all flights of the specified airline
    SELECT connid,
           fldate
      FROM sflight
      INTO TABLE @et_flights
      WHERE carrid = @iv_carrid
      ORDER BY fldate ASCENDING,
               connid ASCENDING.

  ENDMETHOD.

ENDCLASS.
