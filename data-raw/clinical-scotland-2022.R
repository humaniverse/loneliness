# Read csv
clinical_scotland_2022 <- read.csv("inst/extdata/clinical_scotland_2022.csv")

# Save RDA to data/ folder
usethis::use_data(clinical_scotland_2022, overwrite = TRUE)

