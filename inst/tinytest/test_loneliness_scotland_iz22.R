library(geographr)
library(tidyverse)
pkgload::load_all(".")

# Load dataframe
# Use dummy dataset for now; to be changed when actual data is pushed
loneliness_scotland_iz <-
  dummy_loneliness_scotland_iz22

# ---- Tests: Overall dataframe ----
# Test its class as a tibble data frame
expect_equal(
  class(loneliness_scotland_iz)[1],
  "tbl_df"
)

# Test its dimensions: 1279 interzones, and 4 columns
expect_equal(
  dim(loneliness_scotland_iz),
  c(1279, 4)
)

# ---- Tests: Interzone ----
# Test class
expect_equal(
  class(loneliness_scotland_iz$iz_code11),
  "character"
)

# Test all Interzone codes are there
scotland_iz_codes <-
  lookup_dz11_iz11_ltla20 |>
  distinct(iz11_code)

expect_equal(
  sort(loneliness_scotland_iz$iz_code11),
  sort(scotland_iz_codes$iz11_code)
)

# ---- Tests: Loneliness z-score ----
# Test class
expect_equal(
  class(loneliness_scotland_iz$loneliness_zscore),
  "numeric"
)

# Test all values fall within threshold of sd's (TBD)
mean_loneliness <- mean(loneliness_scotland_iz$loneliness_zscore, na.rm = TRUE)
threshold <- 4 * sd(loneliness_scotland_iz$loneliness_zscore, na.rm = TRUE)

all_within_threshold <-
  all(
    loneliness_scotland_iz$loneliness_zscore >= mean_loneliness - threshold &
      loneliness_scotland_iz$loneliness_zscore <= mean_loneliness + threshold
  )

expect_true(all_within_threshold)

# ---- Tests: Rank ----
# Test class
expect_equal(
  class(loneliness_scotland_iz$rank),
  "numeric"
)

expect_equal(
  sort(loneliness_scotland_iz$rank),
  1:1279
)

# ---- Tests: Deciles ----
# Test class
expect_equal(
  class(loneliness_scotland_iz$deciles),
  "integer"
)

# Test number of values per bin
deciles <- loneliness_scotland_iz$deciles

bin_count <- length(deciles) %/% 10
remainder <- length(deciles) %% 10

expected_counts <- rep(bin_count, 10)
expected_counts[1:remainder] <- expected_counts[1:remainder] + 1

grouped_deciles <-
  loneliness_scotland_iz |>
  group_by(deciles) |>
  summarise(n = n()) |>
  ungroup()

actual_counts <- grouped_deciles$n

expect_equal(
  sort(expected_counts),
  sort(actual_counts)
)
