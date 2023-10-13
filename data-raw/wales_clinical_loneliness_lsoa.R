library(tidyverse)

wales_clinical_loneliness_lsoa <- read.csv("inst/extdata/wales_clinical_loneliness_lsoa.csv")

# Save output as RDA in data/ folder
usethis::use_data(wales_clinical_loneliness_lsoa, overwrite = TRUE)

