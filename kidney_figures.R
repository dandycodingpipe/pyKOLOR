library(dplyr)
library(readr)
library(ggplot2)

renalLoad <- function(tag, path = "Kidney_Measurements/", group) {
  # Construct the pattern to search for files with the specific tag
  
  pattern <- paste0(tag,"_",group, "[0-9]+\\.csv$")
  
  # List all files in the directory
  all_files <- list.files(path, pattern = pattern, full.names = TRUE)
  
  # Function to read a file and add NA rows if needed
  readAndPad <- function(filePath) {
    df <- read_csv(filePath)
    neededRows <- 5 - nrow(df)
    if (neededRows > 0) {
      # Create a tibble of NAs with the same number of columns as df
      padRows <- as_tibble(matrix(NA, ncol = ncol(df), nrow = neededRows))
      colnames(padRows) <- colnames(df)
      # Bind the padRows on top of df
      df <- bind_rows(padRows, df)
    }
    return(df)
  }
  
  vesselStats <- function(data) {
  # Prepare data frames to store the final averages and standard deviations
  averages_df <- data.frame(matrix(ncol = ncol(data[[1]]), nrow = nrow(data[[1]])))
  colnames(averages_df) <- colnames(data[[1]])
  
  std_dev_df <- data.frame(matrix(ncol = ncol(data[[1]]), nrow = nrow(data[[1]])))
  colnames(std_dev_df) <- colnames(data[[1]])
  
  # Iterate over each row
  for(row in 1:nrow(data[[1]])) {
    sums <- vector("numeric", ncol(data[[1]]))
    squared_sums <- vector("numeric", ncol(data[[1]]))
    counts <- rep(0, ncol(data[[1]]))
    
    # Loop through each data frame in the list
    for(df in data) {
      # Check if the row exists in the current data frame
      if(nrow(df) >= row) {
        # Convert the row to numeric
        row_values <- as.numeric(df[row, ])
        sums <- sums + row_values
        squared_sums <- squared_sums + (row_values)^2
        counts <- counts + 1
      }
    }
    
    # Calculate the averages and standard deviations
    averages <- sums / counts
    variances <- (squared_sums - (sums^2 / counts)) / (counts - 1)
    std_devs <- sqrt(variances)
    
    # Store results in the corresponding data frames
    averages_df[row, ] <- averages
    std_dev_df[row, ] <- std_devs
  }
  
  return(list(averages = averages_df, std_devs = std_dev_df))
}
  
  
  # Load each file and store in a list
  data_list <- lapply(all_files, readAndPad)
  
  return(data_list)
}

vesselStats <- function(data) {
  # Prepare data frames to store the final averages and standard deviations
  averages_df <- data.frame(matrix(ncol = ncol(data[[1]]), nrow = nrow(data[[1]])))
  colnames(averages_df) <- colnames(data[[1]])
  
  std_dev_df <- data.frame(matrix(ncol = ncol(data[[1]]), nrow = nrow(data[[1]])))
  colnames(std_dev_df) <- colnames(data[[1]])
  
  # Iterate over each row
  for(row in 1:nrow(data[[1]])) {
    sums <- vector("numeric", ncol(data[[1]]))
    squared_sums <- vector("numeric", ncol(data[[1]]))
    counts <- rep(0, ncol(data[[1]]))
    
    # Loop through each data frame in the list
    for(df in data) {
      # Check if the row exists in the current data frame
      if(nrow(df) >= row) {
        # Convert the row to numeric
        row_values <- as.numeric(df[row, ])
        sums <- sums + row_values
        squared_sums <- squared_sums + (row_values)^2
        counts <- counts + 1
      }
    }
    
    # Calculate the averages and standard deviations
    averages <- sums / counts
    variances <- (squared_sums - (sums^2 / counts)) / (counts - 1)
    std_devs <- sqrt(variances)
    
    # Store results in the corresponding data frames
    averages_df[row, ] <- averages
    std_dev_df[row, ] <- std_devs
  }
  
  return(list(averages = averages_df, std_devs = std_dev_df))
}
  
cortex = renalLoad("r_cortex",path = "Kidney_Measurements/", group = "s")
medulla = renalLoad("r_medulla",path = "Kidney_Measurements/", group = "s")
pelvis = renalLoad("r_pelvis",path = "Kidney_Measurements/", group = "s")
stats_dotarem_c = vesselStats(cortex)
stats_dotarem_m = vesselStats(medulla)
stats_dotarem_r = vesselStats(pelvis)
stats_dotarem_c$averages
stats_dotarem_m$averages
stats_dotarem_r$averages
