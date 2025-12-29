CLASS ltcl_test DEFINITION
  FOR TESTING
  RISK LEVEL HARMLESS
  DURATION SHORT.

  PRIVATE SECTION.
    CLASS-METHODS:
      class_teardown.

    METHODS:
      setup.

    METHODS:
      test_exact_match_customer_id FOR TESTING,
      test_exact_match_name FOR TESTING,
      test_partial_match_customer_id FOR TESTING,
      test_partial_match_name FOR TESTING,
      test_no_match FOR TESTING,
      test_empty_pattern FOR TESTING,
      test_mixed_case_pattern FOR TESTING,
      test_no_data_in_db FOR TESTING.

    TYPES:
      BEGIN OF ty_test_customer_wa,
        customer_id TYPE zcustomer-customer_id,
        name        TYPE zcustomer-name,
      END OF ty_test_customer_wa .
    TYPES:
      tt_test_customers TYPE STANDARD TABLE OF zcustomer WITH EMPTY KEY .

ENDCLASS.


CLASS ltcl_test IMPLEMENTATION.

  METHOD class_teardown.
    DELETE FROM zcustomer WHERE customer_id IN ( '0000000001',
                                                 '0000000002',
                                                 '0000000123',
                                                 '0000000456',
                                                 '0000000789',
                                                 '0000009999'
                                                ).
    COMMIT WORK.
  ENDMETHOD.

  METHOD setup.
    DELETE FROM zcustomer WHERE customer_id IN ( '0000000001',
                                                 '0000000002',
                                                 '0000000123',
                                                 '0000000456',
                                                 '0000000789',
                                                 '0000009999'
                                                ).
    COMMIT WORK.
  ENDMETHOD.


  METHOD test_exact_match_customer_id.
    DATA ls_customer TYPE ty_test_customer_wa.
    ls_customer-customer_id = '0000000001'.
    ls_customer-name = 'Alpha Company'.
    INSERT zcustomer FROM ls_customer.
    COMMIT WORK.

    DATA lv_pattern TYPE string.
    lv_pattern = '0000000001'.
    DATA(lt_results) = z_humaneval_erp_010=>find_by_pattern( iv_pattern = lv_pattern ).

    cl_abap_unit_assert=>assert_equals( act = lines( lt_results ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = lt_results[ 1 ]-customer_id exp = '0000000001' ).
  ENDMETHOD.

  METHOD test_exact_match_name.
    DATA ls_customer TYPE ty_test_customer_wa.
    ls_customer-customer_id = '0000000001'.
    ls_customer-name = 'Alpha Company'.
    INSERT zcustomer FROM ls_customer.
    COMMIT WORK.

    DATA lv_pattern TYPE string.
    lv_pattern = 'alpha company'.
    DATA(lt_results) = z_humaneval_erp_010=>find_by_pattern( iv_pattern = lv_pattern ).

    cl_abap_unit_assert=>assert_equals( act = lines( lt_results ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = lt_results[ 1 ]-name exp = 'Alpha Company' ).
  ENDMETHOD.

  METHOD test_partial_match_customer_id.
    DATA lt_data TYPE tt_test_customers.
    DATA ls_data TYPE ty_test_customer_wa.

    ls_data-customer_id = '0000000001'.
    ls_data-name = 'Alpha Company'.
    APPEND ls_data TO lt_data.

    ls_data-customer_id = '0000000002'.
    ls_data-name = 'Beta Corp'.
    APPEND ls_data TO lt_data.

    INSERT zcustomer FROM TABLE lt_data.
    COMMIT WORK.

    DATA lv_pattern TYPE string.
    lv_pattern = '001'.
    DATA(lt_results) = z_humaneval_erp_010=>find_by_pattern( iv_pattern = lv_pattern ).

    cl_abap_unit_assert=>assert_equals( act = lines( lt_results ) exp = 1 ).
  ENDMETHOD.

  METHOD test_partial_match_name.
    DATA ls_customer TYPE ty_test_customer_wa.
    ls_customer-customer_id = '0000000002'.
    ls_customer-name = 'Beta Corp'.
    INSERT zcustomer FROM ls_customer.
    COMMIT WORK.

    DATA lv_pattern TYPE string.
    lv_pattern = 'corp'.
    DATA(lt_results) = z_humaneval_erp_010=>find_by_pattern( iv_pattern = lv_pattern ).

    cl_abap_unit_assert=>assert_equals( act = lines( lt_results ) exp = 1 ).
  ENDMETHOD.

  METHOD test_no_match.
    DATA lv_pattern TYPE string.
    lv_pattern = '0000000999'.
    DATA(lt_results) = z_humaneval_erp_010=>find_by_pattern( iv_pattern = lv_pattern ).

    cl_abap_unit_assert=>assert_initial( act = lt_results ).
  ENDMETHOD.

  METHOD test_empty_pattern.
    DATA lt_data TYPE tt_test_customers.
    DATA ls_data TYPE ty_test_customer_wa.

    ls_data-customer_id = '0000000001'.
    ls_data-name = 'Alpha Company'.
    APPEND ls_data TO lt_data.

    ls_data-customer_id = '0000009999'.
    ls_data-name = 'Dummy Record'.
    APPEND ls_data TO lt_data.

    INSERT zcustomer FROM TABLE lt_data.
    COMMIT WORK.

    DATA lv_pattern TYPE string.
    lv_pattern = ''.
    DATA(lt_results) = z_humaneval_erp_010=>find_by_pattern( iv_pattern = lv_pattern ).

    cl_abap_unit_assert=>assert_equals( act = lines( lt_results ) exp = 2 ).
  ENDMETHOD.

  METHOD test_mixed_case_pattern.
    DATA ls_customer TYPE ty_test_customer_wa.
    ls_customer-customer_id = '0000000123'.
    ls_customer-name = 'XYZ Corporation'.
    INSERT zcustomer FROM ls_customer.
    COMMIT WORK.

    DATA lv_pattern TYPE string.
    lv_pattern = 'xYz coRp'.
    DATA(lt_results) = z_humaneval_erp_010=>find_by_pattern( iv_pattern = lv_pattern ).

    cl_abap_unit_assert=>assert_equals( act = lines( lt_results ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = lt_results[ 1 ]-customer_id exp = '0000000123' ).
  ENDMETHOD.


  METHOD test_no_data_in_db.
    DATA lv_pattern TYPE string.
    lv_pattern = 'any'.
    DATA(lt_results) = z_humaneval_erp_010=>find_by_pattern( iv_pattern = lv_pattern ).

    cl_abap_unit_assert=>assert_initial( act = lt_results ).
  ENDMETHOD.

ENDCLASS.