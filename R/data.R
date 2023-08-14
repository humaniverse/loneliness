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
"england_cls_loneliness_2020"