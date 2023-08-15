library(tidyverse)

england_cls_loneliness_2020 <- read.csv("inst/extdata/england_cls_loneliness_2020.csv")

# Save output as RDA in data/ folder
usethis::use_data(england_cls_loneliness_2020, overwrite = TRUE)
