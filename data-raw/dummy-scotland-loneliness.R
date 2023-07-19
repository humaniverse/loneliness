library(dplyr)
library(geographr)
library(sf)

iz <- boundaries_iz11 |>
  sf::st_drop_geometry()

# Set seed for reproducibility when generating random loneliness_zscore
set.seed(123)

dummy_scotland_loneliness <- tibble(
  interzone = iz$iz11_name,
  loneliness_zscore = rnorm(length(interzone)),
  ranked = rank(loneliness_zscore),
  deciles = ntile(loneliness_zscore, 10)
)

usethis::use_data(dummy_scotland_loneliness, overwrite = TRUE)
