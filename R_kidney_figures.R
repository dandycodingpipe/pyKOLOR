library(dplyr)
library(readr)
library(ggplot2)
library(tidyverse)

# Adjusted function to load renal data
renalLoad <- function(tag, path = "Kidney_Measurements/", group = "") {
  # Construct the pattern to search for files with the specific tag and group
  pattern <- paste0(tag, "_", group, "[0-9]+\\.csv$")
  
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
  
  # Load each file and store in a list
  data_list <- lapply(all_files, readAndPad)
  
  return(data_list)
}

# Function to calculate stats remains unchanged
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
        
        # Identify non-NA indices
        non_na_indices <- !is.na(row_values)
        
        # Perform calculations only on non-NA values
        sums[non_na_indices] <- sums[non_na_indices] + row_values[non_na_indices]
        squared_sums[non_na_indices] <- squared_sums[non_na_indices] + (row_values[non_na_indices])^2
        counts[non_na_indices] <- counts[non_na_indices] + 1
      }
    }
    
    # Calculate the averages and standard deviations
    averages <- sums / counts
    variances <- (squared_sums - (sums^2 / counts)) / (counts - 1)
    std_devs <- sqrt(variances)
    
    # Handle cases where count is zero to avoid division by zero
    averages[is.na(averages)] <- NA  # Set NA where division by zero occurred
    std_devs[is.na(std_devs)] <- NA
    
    # Store results in the corresponding data frames
    averages_df[row, ] <- averages
    std_dev_df[row, ] <- std_devs
  }
  
  return(list(averages = averages_df, std_devs = std_dev_df))
}


# Loading renal data and generating descriptive stats
cortex_data <- renalLoad("r_cortex", group = "s")
medulla_data <- renalLoad("r_medulla", group = "s")
pelvis_data <- renalLoad("r_pelvis", group = "s")

#aguix ONLY
#correct <-c(1,3,4,5,6,7)
#aguix_cortex_data <- aguix_cortex_data[correct]
#aguix_medulla_data <- aguix_medulla_data[correct]
#aguix_pelvis_data <- aguix_pelvis_data[correct]

adj_cortex <- adjust_and_calculate_CNR(cortex_data)
adj_medulla <- adjust_and_calculate_CNR(medulla_data)
adj_pelvis <- adjust_and_calculate_CNR(pelvis_data)
cortex_stats <- vesselStats(adj_cortex)
medulla_stats <- vesselStats(adj_medulla)
pelvis_stats <- vesselStats(adj_pelvis)

# Function to generate a simple plot for one of the renal areas
plotRenalData <- function(stats, title) {
  plot_data <- stats$averages
  ggplot(plot_data, aes(x = seq_along(Signal_Kedge), y = Signal_Kedge)) +
    geom_line() +
    geom_point() +
    labs(title = title, x = "Time Point", y = "Signal (Kedge)") +
    theme_minimal()
}

library(ggplot2)
library(reshape2) # For melting the data into long format

plotRenalDataBars <- function(stats_list, title, data, ylab, y_breaks) {
  # Assuming Time Points are consistent across datasets
  time_points <- c(0.11, 0.5, 1, 3, 10)  # Adjust if your time points are different
  
  renal_areas <- c("Liver", "Spleen", "Cortex", "Medulla", "Pelvis")  # Specified order here
  #renal_areas <- c("Cortex", "Medulla", "Pelvis") 
  # Prepare data for plotting

  plot_data <- data.frame(
    TimePoint = rep(time_points, times = length(renal_areas)),
    Signal = unlist(lapply(stats_list, function(x) x$averages[[data]])),
    SD = unlist(lapply(stats_list, function(x) x$std_devs[[data]])),
    RenalArea = rep(renal_areas, each = length(time_points))
  )
  
  # Set RenalArea as a factor with the specified order
  plot_data$RenalArea <- factor(plot_data$RenalArea, levels = renal_areas)
  
  # Convert TimePoint to a factor to have discrete bars
  plot_data$TimePoint <- factor(plot_data$TimePoint, levels = as.character(time_points))
  
  gg <- ggplot(plot_data, aes(x = TimePoint, y = Signal, fill = RenalArea)) +
    geom_bar(stat = "identity", position = position_dodge(width = 0.7), width = 0.6) +
    geom_errorbar(aes(ymin = Signal - SD, ymax = Signal + SD), width = 0.2, position = position_dodge(width = 0.7)) +
    scale_fill_manual(values = c("Liver" = "gold", "Spleen" = "hotpink", "Cortex" = "purple", "Medulla" = "orange", "Pelvis" = "lightgreen")) +
    labs(title = title, x = "Time (min)", y = ylab) +
    scale_y_continuous(limits = c(0, 9.5), expand = expansion(mult = c(0.003, 0.006)), breaks = y_breaks) +
    theme_minimal() +
    theme(
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      plot.title = element_text(hjust = 0.5, size = 30),
      legend.title = element_blank(),
      axis.line = element_line(color = "black", size = 1),
      axis.line.x = element_line(color = "black", size = 1),
      axis.line.y = element_line(color = "black", size = 1),
      axis.ticks = element_line(color = "black"),
      axis.title = element_text(size = 30),
      panel.border = element_blank(),
      axis.title.y = element_text(size = 30, margin = margin(r = 20)),
      axis.title.x = element_text(size = 30, margin = margin(t = 20)),
      panel.background = element_rect(fill = "white"),
      axis.text.x = element_text(size = 30),
      axis.text = element_text(size = 30, margin = margin(r = 20), face = "bold")
    ) +
    geom_vline(xintercept = c(2.5, 4.5), linetype = "dotted", color = "black")  # Vertical dotted lines
  
  # Print the plot
  print(gg)
  ggsave("CNR_organs_Kedge_plot.png", plot = gg, width = 2500, height = 2500, units = "px")
  
}

# Ensure your stats_list is correct and includes the ordered data
#stats_list <- list(liver_stats_adjusted, spleen_stats_adjusted, cortex_stats, medulla_stats, pelvis_stats)
stats_list <- list(liver_stats, spleen_stats, cortex_stats, medulla_stats, pelvis_stats)
plotRenalDataBars(stats_list, "Gd K-edge Organ Biodistribution", "Signal_Kedge", "[Gd] (mg/mL)", y_breaks = c(1:10))
plotRenalDataBars(stats_list, "Medulla Enhancement", "Signal_HU", "Hounsfield Units (HU)", y_breaks = c(50,100, 150, 200, 300, 400 ,500, 600))
plotRenalDataBars(stats_list, "CNR Color K-edge Images", "CNR_Kedge", "log10(A.U)",  y_breaks = c(1:14))

