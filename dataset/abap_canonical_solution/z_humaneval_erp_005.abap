CLASS z_humaneval_erp_005 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    " Static method to calculate critical path from database tables
    CLASS-METHODS: calculate_critical_path
      RETURNING
        VALUE(rv_duration) TYPE i.

  PRIVATE SECTION.
    " Internal types for graph processing
    TYPES: BEGIN OF ty_node,
             step_id      TYPE c LENGTH 10,
             duration     TYPE i,
             in_degree    TYPE i,
             max_duration TYPE i,
             predecessors TYPE stringtab,
             successors   TYPE stringtab,
           END OF ty_node,
           tt_nodes TYPE HASHED TABLE OF ty_node WITH UNIQUE KEY step_id.

    " Helper methods
    CLASS-METHODS: build_graph
      RETURNING
        VALUE(rt_nodes) TYPE tt_nodes,

      calculate_longest_path
        CHANGING
          ct_nodes               TYPE tt_nodes
        RETURNING
          VALUE(rv_max_duration) TYPE i.

ENDCLASS.

CLASS z_humaneval_erp_005 IMPLEMENTATION.

  METHOD calculate_critical_path.
    " Build the graph from database tables
    DATA(lt_nodes) = build_graph( ).

    " Calculate longest path using topological sort
    rv_duration = calculate_longest_path(
      CHANGING ct_nodes = lt_nodes
    ).
  ENDMETHOD.

  METHOD build_graph.
    DATA: lv_step TYPE string.

    " Read all manufacturing steps from database
    SELECT step_id, description, duration
      FROM zfs_data
      INTO TABLE @DATA(lt_steps).

    " Initialize nodes from database steps
    LOOP AT lt_steps INTO DATA(ls_step).
      DATA(ls_node) = VALUE ty_node(
        step_id = ls_step-step_id
        duration = ls_step-duration
        in_degree = 0
        max_duration = 0
      ).
      INSERT ls_node INTO TABLE rt_nodes.
    ENDLOOP.

    " Read all dependencies from database
    SELECT from_step, to_step
      FROM zfnet_data
      INTO TABLE @DATA(lt_dependencies).

    " Build adjacency lists and calculate in-degrees
    LOOP AT lt_dependencies INTO DATA(ls_dependency).
      " Add successor to from_step
      READ TABLE rt_nodes ASSIGNING FIELD-SYMBOL(<ls_from_node>)
        WITH KEY step_id = ls_dependency-from_step.
      IF sy-subrc = 0.
        lv_step = ls_dependency-to_step.
        APPEND lv_step TO <ls_from_node>-successors.
      ENDIF.

      " Increment in_degree for to_step and add predecessor
      READ TABLE rt_nodes ASSIGNING FIELD-SYMBOL(<ls_to_node>)
        WITH KEY step_id = ls_dependency-to_step.
      IF sy-subrc = 0.
        <ls_to_node>-in_degree = <ls_to_node>-in_degree + 1.
        lv_step = ls_dependency-from_step.
        APPEND lv_step TO <ls_to_node>-predecessors.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD calculate_longest_path.
    DATA: lt_queue        TYPE TABLE OF string,
          lv_step         TYPE string,
          lv_max_end_time TYPE i.

    " Initialize queue with nodes having in_degree = 0
    LOOP AT ct_nodes ASSIGNING FIELD-SYMBOL(<ls_node>).
      IF <ls_node>-in_degree = 0.
        <ls_node>-max_duration = <ls_node>-duration.
        lv_step = <ls_node>-step_id.
        APPEND lv_step TO lt_queue.
      ENDIF.
    ENDLOOP.

    " Process nodes in topological order
    WHILE lines( lt_queue ) > 0.
      " Dequeue first element
      READ TABLE lt_queue INDEX 1 INTO lv_step.
      DELETE lt_queue INDEX 1.

      " Get current node
      READ TABLE ct_nodes ASSIGNING FIELD-SYMBOL(<ls_current>)
        WITH KEY step_id = lv_step.
      CHECK sy-subrc = 0.

      " Process all successors
      LOOP AT <ls_current>-successors INTO lv_step.
        READ TABLE ct_nodes ASSIGNING FIELD-SYMBOL(<ls_successor>)
          WITH KEY step_id = lv_step.
        CHECK sy-subrc = 0.

        " Update max_duration for successor
        DATA(lv_new_duration) = <ls_current>-max_duration + <ls_successor>-duration.
        IF lv_new_duration > <ls_successor>-max_duration.
          <ls_successor>-max_duration = lv_new_duration.
        ENDIF.

        " Decrease in_degree
        <ls_successor>-in_degree = <ls_successor>-in_degree - 1.

        " If in_degree becomes 0, add to queue
        IF <ls_successor>-in_degree = 0.
          lv_step = <ls_successor>-step_id.
          APPEND lv_step TO lt_queue.
        ENDIF.
      ENDLOOP.
    ENDWHILE.

    " Find maximum duration among all nodes
    rv_max_duration = 0.
    LOOP AT ct_nodes INTO DATA(ls_node).
      IF ls_node-max_duration > rv_max_duration.
        rv_max_duration = ls_node-max_duration.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.