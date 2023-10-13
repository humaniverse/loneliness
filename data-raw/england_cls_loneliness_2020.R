library(tidyverse)

england_cls_loneliness_lsoa <- read.csv("inst/extdata/england_cls_loneliness_lsoa.csv")

# Save output as RDA in data/ folder
usethis::use_data(england_cls_loneliness_lsoa, overwrite = TRUE)
