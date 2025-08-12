define table zcustomer_types {
  key customer_type : abap.char(30) not null;
  type_code         : abap.char(1) not null;
  description       : abap.char(100);

}