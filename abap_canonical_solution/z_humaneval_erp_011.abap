CLASS z_humaneval_erp_011 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.

    " Structure for flight search results
    TYPES: BEGIN OF ty_flight_result,
             airline_name     TYPE char40,
             departure_city   TYPE char20,
             destination_city TYPE char20,
             flight_time      TYPE i,
             available_seats  TYPE i,
           END OF ty_flight_result.

    TYPES: tt_flight_results TYPE STANDARD TABLE OF ty_flight_result WITH EMPTY KEY.

    " Static method for searching available flights
    CLASS-METHODS: get_available_flights
      IMPORTING
        origin_city       TYPE char20
        destination_city  TYPE char20
        flight_date       TYPE dats
      RETURNING
        VALUE(et_results) TYPE tt_flight_results.

ENDCLASS.

CLASS z_humaneval_erp_011 IMPLEMENTATION.

  METHOD get_available_flights.

    DATA: ls_result TYPE ty_flight_result.

    " Select available flights with airline information
    SELECT scarr~carrname AS airline_name,
           spfli~cityfrom AS departure_city,
           spfli~cityto AS destination_city,
           spfli~fltime AS flight_time,
           ( sflight~seatsmax - sflight~seatsocc ) AS available_seats
      FROM sflight
      INNER JOIN spfli ON sflight~carrid = spfli~carrid
                      AND sflight~connid = spfli~connid
      INNER JOIN scarr ON sflight~carrid = scarr~carrid
      WHERE spfli~cityfrom = @origin_city
        AND spfli~cityto = @destination_city
        AND sflight~fldate = @flight_date
        AND ( sflight~seatsmax - sflight~seatsocc ) > 0
      INTO CORRESPONDING FIELDS OF TABLE @et_results.

  ENDMETHOD.

ENDCLASS.