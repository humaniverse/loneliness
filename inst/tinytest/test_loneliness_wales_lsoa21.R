# library(tinytest)
# library(tidyverse)
# pkgload::load_all(".")

# Load files
data(wales_clinical_loneliness_lsoa)
wales_codes_path <- system.file("extdata", "test", "wales_lsoa21_codes.csv", package = "loneliness", mustWork = TRUE)
wales_lsoa_codes <- read.csv(wales_codes_path)


# ---- Tests: Overall dataframe ----
# Test it is a dataframe
expect_equal(
  class(wales_clinical_loneliness_lsoa)[1],
  "data.frame"
)

# Test shape of dataframe - 1,916 LSOAs, 4 columns
expect_equal(
  dim(wales_clinical_loneliness_lsoa),
  c(1917, 4)
)

# Omit NAs for rest of the tests
wales_no_na <- na.omit(wales_clinical_loneliness_lsoa)

# ---- Test DataZones ----
# Test class
expect_equal(
  class(wales_no_na$lsoa21_code),
  "character"
)

# Test all DZ codes are present
expect_equal(
  sort(wales_no_na$dz11_code),
  sort(wales_lsoa_codes$dz11_code)
)

# ---- Tests: Loneliness z-score ----
# Test class
expect_equal(
  class(wales_no_na$loneliness_zscore),
  "numeric"
)

# Test all values fall within threshold of sd's (TBD)

# mean_loneliness <- mean(scotland_clinical_loneliness_dz$loneliness_zscore, na.rm = TRUE)
# threshold <- 4 * sd(scotland_clinical_loneliness_dz$loneliness_zscore, na.rm = TRUE)
#
# all_within_threshold <-
#   all(
#     scotland_clinical_loneliness_dz$loneliness_zscore >= mean_loneliness - threshold &
#       scotland_clinical_loneliness_dz$loneliness_zscore <= mean_loneliness + threshold
#   )
#
# expect_true(all_within_threshold)

# ---- Tests: Rank ----
# Test class
expect_equal(
  class(wales_no_na$rank),
  "numeric"
)

# Compute ranks with same tie handling method to test actual ranks
expected_ranks <-
  rank(wales_no_na$loneliness_zscore, ties.method = "average")

expect_equal(
  wales_no_na$rank,
  expected_ranks,
  na.rm = TRUE
)

# ---- Tests: Deciles ----
# Test class
expect_equal(
  class(wales_no_na$deciles),
  "integer"
)

# Test number of values per bin
deciles <- wales_no_na$deciles

bin_count <- length(deciles) %/% 10
remainder <- length(deciles) %% 10

expected_counts <- rep(bin_count, 10)
expected_counts[1:remainder] <- expected_counts[1:remainder] + 1

actual_counts <- as.vector(table(wales_no_na$deciles))

expect_equal(
  sort(expected_counts),
  sort(actual_counts)
)
