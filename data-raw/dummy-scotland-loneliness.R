library(dplyr)

dummy_scotland_loneliness <- tibble(
  area_name = NA,
  zscore = NA,
  rank =  NA,
  decile = NA
)

usethis::use_data(dummy_scotland_loneliness, overwrite = TRUE)
