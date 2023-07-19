pkgload::load_all(".")

# Load dataframe
# For now, use dummy dataset, to be changed when data is pushed
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

# ---- Tests: Loneliness z-score ----
# Test class
expect_equal(
  class(loneliness_scotland_iz$loneliness_zscore),
  "numeric"
)

# Test all values fall within threshold of sd's

# ---- Tests: Rank ----
# Test class
expect_equal(
  class(loneliness_scotland_iz$rank),
  "numeric"
)

# Test unique ranks, from 1 to 1279. If tie: rank is average of values tied

# ---- Tests: Deciles ----
# Test class
expect_equal(
  class(loneliness_scotland_iz$deciles),
  "integer"
)

# Test number of values per bin
