define table zcountry_codes {
  key country_name : abap.char(50) not null;
  country_code     : abap.char(4) not null;
  iso_code         : abap.char(2);
  phone_prefix     : abap.char(10);

}