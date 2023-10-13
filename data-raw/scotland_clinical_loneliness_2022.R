library(tidyverse)

scotland_prescription_loneliness_2022 <- read.csv("inst/extdata/scotland_prescription_loneliness_2022.csv")

# Save output as RDA in data/ folder
usethis::use_data(scotland_prescription_loneliness_2022, overwrite = TRUE)
