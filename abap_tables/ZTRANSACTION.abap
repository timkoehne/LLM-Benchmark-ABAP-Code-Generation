define table ztransaction {
  key id           : abap.int4 not null;
  mat_id           : abap.char(20) not null;
  transaction_type : abap.char(20) not null;
  transaction_date : abap.dats not null;
  amount           : abap.int4 not null;

}