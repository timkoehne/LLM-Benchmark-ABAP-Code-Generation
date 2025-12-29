define table zsales_aggr {
  key zname     : abap.char(20) not null;
  key zarticle  : abap.char(10) not null;
  key zcurrency : abap.cuky not null;
  @Semantics.amount.currencyCode : 'zsales_aggr.zcurrency'
  zrev          : abap.curr(13,2) not null;

}