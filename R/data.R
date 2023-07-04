#'  Clinical Measures of Loneliness, Scotland - 2022
#'
#' An index for clinical loneliness measures in Scotland for 2022. The index is calculated using GP prescription data for
#' five conditions where loneliness has been shown to be a risk factor: Alzheimer's, depression,
#' high blood pressure, anxiety and insomnia.
#'
#'
#' @format A data frame with 733 rows and 4 variables:
#' \describe{
#'   \item{postcode}{Postcode}
#'   \item{loneliness_zscore}{A loneliness score calculated by summing the z scores of GP prescriptions for loneliness associated illnesses}
#'   \item{ranked}{The rank of each postcode according to its loneliness_zscore, in ascending order}
#'   \item{deciles}{The decile rank of each postcode according to its loneliness_zscore, split into 10 equal sized bins, in ascending order}
#' }
#'
#' @source
#'   \itemize{
#'     \item \url{https://www.opendata.nhs.scot/dataset/prescriptions-in-the-community}
#'     \item \url{https://www.opendata.nhs.scot/dataset/gp-practice-contact-details-and-list-sizes}
#'   }

"clinical_scotland_2022"
