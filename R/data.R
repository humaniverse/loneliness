#' England Loneliness Scores from Community Life Survey 2020-21
#'
#' A dataset with scores for loneliness at LSOA level.
#' Scores are a percentage of answers to a direct question on loneliness 
#' asked in the Community Life Survey conducted by the DCSM.
#' The question is "How often do you feel lonely?" and the percentage represents
#' responses of "Often/always & some of the time".
#' ...
#'
#' @format A data frame with 33,755 rows and 2 variables:
#' \describe{
#'   \item{lsoa21_code}{Lower Super Output Area 2021 Code}
#'   \item{perc}{Percentage that respond "Often/always & some of the time" to
#'   "How often do you feel lonely?"}
#'   ...
#' }
#' @source \url{https://www.gov.uk/government/statistical-data-sets/dcms-community-life-survey-ad-hoc-statistical-releases}
"england_cls_loneliness_lsoa"

#' Northern Ireland Loneliness Scores from GP prescription data, 2022
#'
#' A dataset with scores for loneliness at SDZ level based on GP prescription data.
#' The approach and code to develop this index is based on the 
#' Office for National Statistics' Data Science Campus Loneliness Prescription Index.
#'
#' @format A data frame with 850 rows and 4 variables:
#' \describe{
#'   \item{sdz21_code}{Super Data Zone Code}
#'   \item{loneliness_zscore}{Loneliness score}
#'   \item{rank}{Rank of loneliness score}
#'   \item{deciles}{Loneliness score deciled}
#'  ...
#' }
#' @source \url{https://www.data.gov.uk}
"ni_clinical_loneliness_sdz"

#' Scotland Loneliness Scores from GP prescription data, 2022
#'
#' A dataset with scores for loneliness at IZ level based on GP prescription data.
#' The approach and code to develop this index is based on the 
#' Office for National Statistics' Data Science Campus Loneliness Prescription Index.
#'
#' @format A data frame with 1,279 rows and 4 variables:
#' \describe{
#'   \item{iz11_code}{Intermediate Zone Code}
#'   \item{loneliness_zscore}{Loneliness score}
#'   \item{rank}{Rank of loneliness score}
#'   \item{deciles}{Loneliness score deciled}
#'   ...
#'  }
#' @source \url{https://www.opendata.nhs.scot}
"scotland_clinical_loneliness_dz"

#' Wales Loneliness Scores from GP prescription data, 2022
#'
#' A dataset with scores for loneliness at LSOA level based on GP prescription data.
#' The approach and code to develop this index is based on the 
#' Office for National Statistics' Data Science Campus Loneliness Prescription Index.
#'
#' @format A data frame with 1,917 rows and 4 variables:
#' \describe{
#'   \item{lsoa21_code}{Lower Super Output Area Code}
#'   \item{loneliness_zscore}{Loneliness score}
#'   \item{rank}{Rank of loneliness score}
#'   \item{deciles}{Loneliness score deciled}
#'   ...
#'  }
#' @source \url{https://nwssp.nhs.wales/}
"wales_clinical_loneliness_lsoa"
