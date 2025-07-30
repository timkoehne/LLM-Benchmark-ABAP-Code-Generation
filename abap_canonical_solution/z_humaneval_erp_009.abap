CLASS z_humaneval_erp_009 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    TYPES: BEGIN OF ty_sales_position,
             zid       TYPE i,
             zname     TYPE c LENGTH 20,
             zarticle  TYPE c LENGTH 10,
             zcurrency TYPE c LENGTH 5,
             zrev      TYPE p LENGTH 8 DECIMALS 2,
           END OF ty_sales_position,
           tt_sales_positions TYPE TABLE OF ty_sales_position.

    TYPES: BEGIN OF ty_sales_aggregated,
             zname     TYPE c LENGTH 20,
             zarticle  TYPE c LENGTH 10,
             zcurrency TYPE c LENGTH 5,
             zrev      TYPE p LENGTH 8 DECIMALS 2,
           END OF ty_sales_aggregated,
           tt_sales_aggregated TYPE TABLE OF ty_sales_aggregated.

    CLASS-METHODS: process_sales_aggregation
      RETURNING VALUE(rv_success) TYPE abap_bool.

  PRIVATE SECTION.
    TYPES: BEGIN OF ty_aggregation_key,
             zname     TYPE c LENGTH 20,
             zarticle  TYPE c LENGTH 10,
             zcurrency TYPE c LENGTH 5,
           END OF ty_aggregation_key,
           tt_aggregation_keys TYPE SORTED TABLE OF ty_aggregation_key
                               WITH UNIQUE KEY zname zarticle zcurrency.

ENDCLASS.

CLASS z_humaneval_erp_009 IMPLEMENTATION.

  METHOD process_sales_aggregation.
    DATA: lt_sales_positions  TYPE tt_sales_positions,
          lt_sales_aggregated TYPE TABLE OF zsales_aggr,
          lt_temp_aggregated  TYPE SORTED TABLE OF zsales_aggr
                              WITH UNIQUE KEY zname zarticle zcurrency.

    " Initialize return value
    rv_success = abap_false.

    " Clear target table first with proper commit
    DELETE FROM zsales_aggr.
    COMMIT WORK.

    " Read all sales positions from source table
    SELECT zid, zname, zarticle, zcurrency, zrev
      FROM zsales_positions
      INTO TABLE @lt_sales_positions.

    IF sy-subrc <> 0 OR lines( lt_sales_positions ) = 0.
      " No sales positions found - this is still considered success
      rv_success = abap_true.
      RETURN.
    ENDIF.

    " Aggregate sales data by salesperson and article
    LOOP AT lt_sales_positions INTO DATA(ls_sales_position).
      " Try to read existing aggregated entry
      READ TABLE lt_temp_aggregated INTO DATA(ls_temp_aggregated)
        WITH KEY zname     = ls_sales_position-zname
                 zarticle  = ls_sales_position-zarticle
                 zcurrency = ls_sales_position-zcurrency.

      IF sy-subrc = 0.
        " Entry exists - add revenue to existing amount
        ls_temp_aggregated-zrev = ls_temp_aggregated-zrev + ls_sales_position-zrev.
        MODIFY TABLE lt_temp_aggregated FROM ls_temp_aggregated.
      ELSE.
        " New entry - create aggregated record
        DATA(ls_new_aggregated) = VALUE zsales_aggr(
          zname     = ls_sales_position-zname
          zarticle  = ls_sales_position-zarticle
          zcurrency = ls_sales_position-zcurrency
          zrev      = ls_sales_position-zrev
        ).
        INSERT ls_new_aggregated INTO TABLE lt_temp_aggregated.
      ENDIF.
    ENDLOOP.

    " Convert sorted table to standard table for database insert
    LOOP AT lt_temp_aggregated INTO DATA(ls_aggregated).
      APPEND ls_aggregated TO lt_sales_aggregated.
    ENDLOOP.

    " Insert aggregated data into target table
    IF lines( lt_sales_aggregated ) > 0.
      INSERT zsales_aggr FROM TABLE @lt_sales_aggregated.
      IF sy-subrc = 0.
        COMMIT WORK.
        rv_success = abap_true.
      ELSE.
        ROLLBACK WORK.
      ENDIF.
    ELSE.
      " Empty result set is also considered success
      rv_success = abap_true.
    ENDIF.

  ENDMETHOD.

ENDCLASS.
