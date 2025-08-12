define table zsales_positions {
  key zid   : abap.int4 not null;
  zname     : abap.char(20) not null;
  zarticle  : abap.char(10) not null;
  zcurrency : abap.cuky not null;
  @Semantics.amount.currencyCode : 'zsales_positions.zcurrency'
  zrev      : abap.curr(13,2) not null;

}