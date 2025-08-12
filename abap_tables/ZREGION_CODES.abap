define table zregion_codes {
  key country_code : abap.char(4) not null;
  key region_name  : abap.char(100) not null;
  region_code      : abap.char(2) not null;
  region_type      : abap.char(20);

}