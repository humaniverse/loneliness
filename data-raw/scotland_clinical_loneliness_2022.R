library(tidyverse)

scotland_clinical_loneliness_dz <- read.csv("inst/extdata/scotland_clinical_loneliness_dz.csv")

# Save output as RDA in data/ folder
usethis::use_data(scotland_clinical_loneliness_dz, overwrite = TRUE)
