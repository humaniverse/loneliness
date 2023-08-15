# pkgload::load_all(".")

# Use dummy dataset for now; to be changed when actual data is pushed
data(dummy_loneliness_scotland_iz22)
scotland_iz_codes_path <- system.file("extdata", "scotland_iz_codes.csv", package = "loneliness", mustWork = TRUE)
scotland_iz_codes <- read.csv(scotland_iz_codes_path)


# ---- Tests: Overall dataframe ----
# Test its class as a tibble data frame
expect_equal(
  class(dummy_loneliness_scotland_iz22)[1],
  "tbl_df"
)

# Test its dimensions: 1279 interzones, and 4 columns
expect_equal(
  dim(dummy_loneliness_scotland_iz22),
  c(1279, 4)
)

# ---- Tests: Interzone ----
# Test class
expect_equal(
  class(dummy_loneliness_scotland_iz22$iz_code11),
  "character"
)

# Test all Interzone codes are there
expect_equal(
  sort(dummy_loneliness_scotland_iz22$iz_code11),
  sort(scotland_iz_codes$iz11_code)
)

# ---- Tests: Loneliness z-score ----
# Test class
expect_equal(
  class(dummy_loneliness_scotland_iz22$loneliness_zscore),
  "numeric"
)

# Test all values fall within threshold of sd's (TBD)
mean_loneliness <- mean(dummy_loneliness_scotland_iz22$loneliness_zscore, na.rm = TRUE)
threshold <- 4 * sd(dummy_loneliness_scotland_iz22$loneliness_zscore, na.rm = TRUE)

all_within_threshold <-
  all(
    dummy_loneliness_scotland_iz22$loneliness_zscore >= mean_loneliness - threshold &
      dummy_loneliness_scotland_iz22$loneliness_zscore <= mean_loneliness + threshold
  )

expect_true(all_within_threshold)

# ---- Tests: Rank ----
# Test class
expect_equal(
  class(dummy_loneliness_scotland_iz22$rank),
  "numeric"
)

# Compute ranks with same tie handling method to test actual ranks
expected_ranks <-
  rank(dummy_loneliness_scotland_iz22$loneliness_zscore, ties.method = "average")

expect_equal(
  dummy_loneliness_scotland_iz22$rank,
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
