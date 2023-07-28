library(geographr)
library(feather)

lookup_11 <- lookup_postcode_oa11_lsoa11_msoa11_ltla20

write_feather(lookup_11, "inst/extdata/lookup_11.feather")
