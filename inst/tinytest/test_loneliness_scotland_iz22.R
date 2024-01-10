library(tinytest)
library(tidyverse)
pkgload::load_all(".")

# Load files
data(scotland_clinical_loneliness_dz)
scotland_dz_codes_path <- system.file("extdata", "test", "scotland_dz11_codes.csv", package = "loneliness", mustWork = TRUE)
scotland_dz_codes <- read.csv(scotland_dz_codes_path)


# ---- Tests: Overall dataframe ----
# Test it is a dataframe
expect_equal(
  class(scotland_clinical_loneliness_dz)[1],
  "data.frame"
)

# Test shape of dataframe - 6,976 DZs, 4 columns
expect_equal(
  dim(scotland_clinical_loneliness_dz),
  c(6976, 4)
)

# ---- Test DataZones ----
# Test class
expect_equal(
  class(scotland_clinical_loneliness_dz$dz11_code),
  "character"
)

# Test all DZ codes are present
expect_equal(
  sort(scotland_clinical_loneliness_dz$dz11_code),
  sort(scotland_dz_codes$dz11_code)
)

# ---- Tests: Loneliness z-score ----
# Test class
expect_equal(
  class(scotland_clinical_loneliness_dz$loneliness_zscore),
  "numeric"
)

# Test all values fall within threshold of sd's (TBD)
mean_loneliness <- mean(scotland_clinical_loneliness_dz$loneliness_zscore, na.rm = TRUE)
threshold <- 4 * sd(scotland_clinical_loneliness_dz$loneliness_zscore, na.rm = TRUE)

all_within_threshold <-
  all(
    scotland_clinical_loneliness_dz$loneliness_zscore >= mean_loneliness - threshold &
      scotland_clinical_loneliness_dz$loneliness_zscore <= mean_loneliness + threshold
  )

expect_true(all_within_threshold)

# ---- Tests: Rank ----
# Test class
expect_equal(
  class(scotland_clinical_loneliness_dz$rank),
  "numeric"
)

# Compute ranks with same tie handling method to test actual ranks
expected_ranks <-
  rank(scotland_clinical_loneliness_dz$loneliness_zscore, ties.method = "average")

expect_equal(
  scotland_clinical_loneliness_dz$rank,
  expected_ranks
)

# ---- Tests: Deciles ----
# Test class
expect_equal(
  class(dummy_loneliness_scotland_iz22$deciles),
  "integer"
)

# Test number of values per bin
deciles <- dummy_loneliness_scotland_iz22$deciles

bin_count <- length(deciles) %/% 10
remainder <- length(deciles) %% 10

expected_counts <- rep(bin_count, 10)
expected_counts[1:remainder] <- expected_counts[1:remainder] + 1

actual_counts <- as.vector(table(dummy_loneliness_scotland_iz22$deciles))

expect_equal(
  sort(expected_counts),
  sort(actual_counts)
)
