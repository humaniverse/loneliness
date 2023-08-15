library(geographr)
library(feather)

geographr_lookup_feather <- function() {
    lookup_11 <- lookup_postcode_oa11_lsoa11_msoa11_ltla20
    lookup_21 <- lookup_lsoa11_lsoa21_ltla22

    write_feather(lookup_11, "inst/extdata/lookup_11.feather")
    write_feather(lookup_21, "inst/extdata/lookup_21.feather")
}

#geographr_lookup_feather()
