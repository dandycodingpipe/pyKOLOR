# angio statistics and figure generation script

library(dplyr)
library(readr)
library(ggplot2)

# load descending thoracic aorta "DTA"
DTA_data <- vesselLoad("DTA")
DTA_stats <- vesselStats(DTA_data)

# load suprarenal abdominal aorta "SAA"
SAA_data <- vesselLoad("SAA")
SAA_stats <- vesselStats(SAA_data)

# load infra renal aorta "IRA"
IRA_data <- vesselLoad("IRA")
IRA_stats <- vesselStats(IRA_data)

# load left renal artery "LRA"
LRA_data <- vesselLoad("LRA")
LRA_stats <- vesselStats(LRA_data)

# load right renal artery "RRA"
RRA_data <- vesselLoad("RRA")
RRA_stats <- vesselStats(RRA_data)


# load inferior vena cava "IVC"
IVC_data <- vesselLoad("IVC")
IVC_stats <- vesselStats(IVC_data)


vesselLoad <- function(tag, path = "Measurements/") {
  # Construct the pattern to search for files with the specific tag
  pattern <- paste0(tag, "_s[0-9]+\\.csv$")
  
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

x = c(0.11, 0.5, 1, 3, 10)
# angio figure generator function
plot(x, IVC_stats[[1]]$Signal_Kedge)


library(ggplot2)

generateAngioPlot <- function(stats_list, column_name, title, x_label, y_label) {
  # Prepare data for plotting
  plot_data <- data.frame(X = c(0.11, 0.5, 1, 3, 10))
  vessel_names <- c("DTA", "SAA", "IRA", "LRA", "RRA", "IVC")
  
  for (i in seq_along(stats_list)) {
    vessel_stats <- stats_list[[i]]
    plot_data[[paste0(vessel_names[i], "_mean")]] <- vessel_stats$averages[[column_name]]
  }
  
  # Melt the data for ggplot, focusing only on mean values
  plot_data_long <- reshape2::melt(plot_data, id.vars = "X", 
                                   variable.name = "Vessel_Stat", value.name = "Value")
  plot_data_long$Vessel <- gsub("_mean$", "", plot_data_long$Vessel_Stat)
  
  # Plot
  ggplot(plot_data_long, aes(x = X, y = Value, group = Vessel, color = Vessel)) +
    geom_line(size = 2) +  # Thicker lines
    geom_point(size = 5) +  # Larger points
    scale_x_continuous(breaks = plot_data$X, labels = as.character(plot_data$X)) +  # Display discrete X values
    scale_color_manual(values = rainbow(length(vessel_names))) +
    labs(title = title, x = x_label, y = y_label) +
    theme_minimal() +
    theme(legend.title = element_blank(),
          plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),  # Centered and bold title
          axis.title = element_text(size = 12),
          axis.text = element_text(size = 10),
          legend.position = "bottom") +
    guides(colour = guide_legend(override.aes = list(size=6)))  # Adjust legend key sizes
}

# Example usage
stats_list <- list(DTA_stats, SAA_stats, IRA_stats, LRA_stats, RRA_stats, IVC_stats)
generateAngioPlot(stats_list, "CNR_HU", "Vessel CNR (Conventional)", "Minutes", "CNR")








plot_data <- data.frame(X = c(0.11, 0.5, 1, 3, 10))
vessel_names <- c("IRA", "LRA", "RRA")
vessel_names <- c("IVC", "DTA", "SAA")
column_name = "Signal_Kedge"
for (i in seq_along(stats_list)) {
  vessel_stats <- stats_list[[i]]
  plot_data[[paste0(vessel_names[i], "_mean")]] <- vessel_stats$averages[[column_name]]
  plot_data[[paste0(vessel_names[i], "_std")]] <- vessel_stats$std_devs[[column_name]]
}

# Melt the data for ggplot
plot_data_long <- reshape2::melt(plot_data, id.vars = "X", 
                                 variable.name = "Vessel_Stat", value.name = "Value")
plot_data_long$Vessel <- gsub("(_mean|_std)$", "", plot_data_long$Vessel_Stat)
plot_data_long$Stat_Type <- ifelse(grepl("_mean$", plot_data_long$Vessel_Stat), "Mean", "Std")




# Filter for mean and standard deviation values
mean_data <- plot_data_long %>% filter(Stat_Type == "Mean")
std_data <- plot_data_long %>% filter(Stat_Type == "Std")

# Merge mean and std data frames by X and Vessel
plot_data <- merge(mean_data, std_data, by = c("X", "Vessel"), suffixes = c("_mean", "_std"))

# Calculate ymin and ymax for error bars
plot_data$ymin <- plot_data$Value_mean - plot_data$Value_std
plot_data$ymax <- plot_data$Value_mean + plot_data$Value_std

# Plot
ggplot(plot_data, aes(x = X, y = Value_mean, color = Vessel)) +
  geom_line(aes(group = Vessel)) +
  geom_point() +
  geom_errorbar(aes(ymin = ymin, ymax = ymax), width = 0.1) +
  labs(x = "Your X-axis Label", y = "Your Y-axis Label", title = "Your Title") +
  theme_minimal()

