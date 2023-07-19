pkgload::load_all(".")

# Load dataframe
# For now, use dummy dataset, to be changed when data is pushed
loneliness_scotland_iz <-
  dummy_loneliness_scotland_iz22

# Check its class as a tibble data frame
expect_equal(
  class(loneliness_scotland_iz)[1],
  "tbl_df"
)

# Check its dimensions: 1279 interzones, and 4 columns
expect_equal(
  dim(loneliness_scotland_iz),
  c(1279, 4)
)
