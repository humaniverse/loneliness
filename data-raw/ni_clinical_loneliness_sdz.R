library(tidyverse)

ni_clinical_loneliness_sdz <- read.csv("inst/extdata/ni_clinical_loneliness_sdz.csv")

# Save output as RDA in data/ folder
usethis::use_data(ni_clinical_loneliness_sdz, overwrite = TRUE)

