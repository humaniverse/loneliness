library(dplyr)
library(geographr)
library(sf)

iz <- boundaries_iz11 |>
  sf::st_drop_geometry()

# Set seed for reproducibility when generating random loneliness_zscore
set.seed(123)

dummy_loneliness_scotland_iz22 <- tibble(
  iz_code11 = iz$iz11_code,
  loneliness_zscore = rnorm(length(iz_code11)),
  rank = rank(loneliness_zscore),
  deciles = ntile(loneliness_zscore, 10)
)

usethis::use_data(dummy_loneliness_scotland_iz22, overwrite = TRUE)
