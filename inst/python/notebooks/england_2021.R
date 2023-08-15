# ---- Load libs and helpers ----
library(tidyverse)
library(geographr)
library(httr2)
library(readODS)

download_file <-
  function(url, file_extension) {
    stopifnot(
      !missing(url),
      !missing(file_extension),
      is.character(url),
      is.character(file_extension)
    )

    temp_path <- tempfile(fileext = file_extension)

    httr2::request(url) |>
      httr2::req_perform(path = temp_path)

    return(temp_path)
  }

# ---- Community Life Survery (CLS) ----
# Source: https://www.gov.uk/government/statistical-data-sets/dcms-community-life-survey-ad-hoc-statistical-releases
url <- "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1149882/Community_Life_Survey_-_Strength_of_community_variables_by_Output_Area_Classifications_2017_18_to_2020_21.ods"

download <- download_file(url, ".ods")

raw <- read_ods(
  download,
  sheet = "A6",
  range = "A27:AC28"
)

cls <- raw |>
  select(-Question:-Metric) |>
  mutate(`OAC group - 7b` = NA_integer_) |>
  pivot_longer(cols = everything()) |>
  rename(oac_11 = name, percent_lonely = value) |>
  mutate(oac_11 = str_sub(oac_11, -2))

# ---- 2011 LSOA lookups ----
# Source: https://www.ons.gov.uk/methodology/geography/geographicalproducts/areaclassifications/2011areaclassifications/datasets
url <- "https://www.ons.gov.uk/file?uri=/methodology/geography/geographicalproducts/areaclassifications/2011areaclassifications/datasets/2011oacclustersandnamescsvv3.zip"

download <- download_file(url, ".zip")

download |>
  unzip(exdir = tempdir())

lookup_oa11_oac <- read_csv(
  file.path(tempdir(), "2011 OAC Clusters and Names Excel v3.csv")
) |>
  select(oac_11 = `Group Code`, oa11_code = `Output Area Code`)

cls_oa <- cls |>
  left_join(lookup_oa11_oac)

lookup_lsoa11_oa11 <- lookup_postcode_oa11_lsoa11_msoa11_ltla20 |>
  distinct(lsoa11_code, oa11_code) |>
  filter(str_detect(lsoa11_code, "^E"))

cls_lsoa11 <- lookup_lsoa11_oa11 |>
  left_join(cls_oa) |>
  summarise(
    percent_lonely = mean(percent_lonely, na.rm = TRUE),
    .by = lsoa11_code
  )