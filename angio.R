# angio statistics and figure generation script

library(dplyr)
library(readr)
library(ggplot2)


vesselLoad <- function(tag, path = "Vessel_Measurements/") {
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


# load descending thoracic aorta "DTA"
DTA_data <- vesselLoad("DTA")
DTA_stats <- vesselStats(DTA_data)

# load suprarenal abdominal aorta "SAA"
SAA_data <- vesselLoad("SAA")
SAA_stats <- vesselStats(SAA_data)

# load infra renal aorta "IRA"
IRA_data <- vesselLoad("IRA")
IRA_stats <- vesselStats(IRA_data)

# load inferior vena cava "IVC"
IVC_data <- vesselLoad("IVC")
# setting signal of IVC to zero because this is the blood pool expansion effect in the vein, its an incomplete concentration. Salim and I discussed this. These will probably need to be redone...
#IVC_data[[4]]$Signal_Kedge[1] = 0
#IVC_data[[5]]$Signal_Kedge[1] = 0
#IVC_data[[4]]$Signal_HU[1] = 78
#IVC_data[[5]]$Signal_HU[1] = 70

IVC_stats <- vesselStats(IVC_data)



# load infra renal vena cava "IRIVC"
IRVC_data <- vesselLoad("IRVC")
IRVC_stats <- vesselStats(IRVC_data)


generateAngioBarsWithError <- function(stats_list, column_name, title, x_label, y_label, y_breaks) {
  # Assuming Time Points are consistent across datasets
  time_points <- factor(c(0.11, 0.5, 1, 3, 10)) # Convert to factor for discrete axis
  
  vessel_names <- c("SAA", "IRA", "IVC", "IRVC")
  colors <- c("SAA" = "red", "IRA" = "pink", "IVC" = "blue", "IRVC" = "lightblue")
  
  # Prepare data for plotting
  plot_data <- expand.grid(TimePoint = time_points, Vessel = vessel_names)
  plot_data$Signal <- unlist(lapply(stats_list, function(x) x$averages[[column_name]]))
  plot_data$SD <- unlist(lapply(stats_list, function(x) x$std_devs[[column_name]]))
  
  gg <- ggplot(plot_data, aes(x = TimePoint, y = Signal, fill = Vessel, group = Vessel)) +
    geom_bar(stat = "identity", position = position_dodge(width = 0.7), width = 0.6) +
    geom_errorbar(aes(ymin = pmax(Signal - SD, 0), ymax = Signal + SD), width = 0.2, position = position_dodge(width = 0.7)) +
    scale_fill_manual(values = colors) +
    labs(title = title, x = x_label, y = y_label) +
    scale_y_continuous(expand = expansion(mult = c(0.003, 0.006)), breaks = y_breaks) +
    theme_minimal() +
    theme(
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      plot.title = element_text(hjust = 0.5), 
      legend.title = element_blank(), 
      axis.line = element_line(color="black", size = 1),
      axis.line.x = element_line(color = "black", size = 1),
      axis.line.y = element_line(color = "black", size = 1),
      axis.ticks = element_line(color = "black"), axis.title = element_text(size = 32),
      panel.border = element_blank(),
      axis.title.y = element_text(size = 18, margin = margin(r = 20)),
      axis.title.x = element_text(size = 18, margin = margin(t = 20)),
      panel.background = element_rect(fill = "white"), axis.text.x = element_text(size = 14),
      axis.text = element_text(size = 14, margin = margin(r = 20), face = "bold" )
    )+
    scale_x_discrete(name = x_label) +
    geom_vline(xintercept = c(2.5, 4.5), linetype = "dotted", color = "black") # Vertical dotted lines
  
  # Print the plot
  print(gg)
}

# Example usage
stats_list <- list(SAA_stats, IRA_stats, IVC_stats, IRVC_stats)
generateAngioBarsWithError(stats_list, "Signal_HU", "Conventional CT Angiography", "Time (min)", "Hounsfield Units (HU)",  y_breaks = c(100, 200, 300, 400 ,500, 600))
generateAngioBarsWithError(stats_list, "Signal_Kedge", "Gd K-edge Angiography", "Time (min)", "[Gd] (mg/mL)", y_breaks = c(1:10))
