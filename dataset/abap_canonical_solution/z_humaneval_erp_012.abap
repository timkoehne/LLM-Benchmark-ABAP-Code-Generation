CLASS z_humaneval_erp_012 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.

    " Structure for returning airline revenue data
    TYPES: BEGIN OF ty_airline_revenue,
             carrname      TYPE scarr-carrname,
             total_revenue TYPE sbook-forcuram,
           END OF ty_airline_revenue,
           tt_airline_revenue TYPE TABLE OF ty_airline_revenue WITH EMPTY KEY.

    CLASS-METHODS: get_total_revenue_by_airline
      RETURNING VALUE(et_result) TYPE tt_airline_revenue.

  PROTECTED SECTION.
  PRIVATE SECTION.

ENDCLASS.

CLASS z_humaneval_erp_012 IMPLEMENTATION.

  METHOD get_total_revenue_by_airline.

    DATA: lt_revenue_data TYPE TABLE OF ty_airline_revenue,
          ls_revenue_data TYPE ty_airline_revenue.

    " Select airline name and sum of booking amounts
    " Join SCARR (airline master) with SBOOK (bookings) tables
    SELECT s~carrname,
           SUM( b~forcuram ) AS total_revenue
      FROM scarr AS s
      INNER JOIN sbook AS b ON s~carrid = b~carrid
      INTO CORRESPONDING FIELDS OF TABLE @lt_revenue_data
      GROUP BY s~carrname
      ORDER BY s~carrname.

    " Return the result
    et_result = lt_revenue_data.

  ENDMETHOD.

ENDCLASS.