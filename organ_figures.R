template_df = data.frame("t" = c(0.11, 0.5, 1, 3, 10), "hu" = c(1:5), "hu_std" = c(1:5), "gd" = c(1:5), "gd_std"= c(1:5))

spleen = template_df

spleen$hu = c(154.0504762,
              125.5148997,
              108.4500961,
              88.92600251,
              80.52978279
              )

spleen$hu_std = c(46.66235895,
                  17.54330199,
                  14.82387967,
                  18.27891114,
                  9.606424392
                  )
  
spleen$gd = c(1.2233714,
              0.616890248,
              0.454237084,
              0.254441528,
              0.060972065)

spleen$gd_std = c(0.78218339,
                  0.237945425,
                  0.189790326,
                  0.210977729,
                  0.070839551
                  )
  

liver = template_df
liver$hu = c(75.85445551,
             101.4115567,
             99.06963241,
             93.74984684,
             79.63147154
             
)
liver$hu_std = c(7.664916337,
                 14.33758501,
                 13.32598704,
                 10.84857957,
                 11.94766289
                 )

liver$gd = c(0.000952333,
             0.419717906,
             0.376348649,
             0.254458647,
             0.050097744
             
)
liver$gd_std = c(0.002857,
                 0.22874234,
                 0.208093603,
                 0.149619852,
                 0.062815978
                 
)

# Create lists for averages and standard deviations for spleen and liver
spleen_stats <- list(
  averages = data.frame(
    t = spleen$t,
    Signal_HU = spleen$hu,
    Signal_Kedge = spleen$gd
  ),
  std_devs = data.frame(
    t = spleen$t,
    Signal_HU = spleen$hu_std,
    Signal_Kedge = spleen$gd_std
  )
)

liver_stats <- list(
  averages = data.frame(
    t = liver$t,
    Signal_HU = liver$hu,
    Signal_Kedge = liver$gd
  ),
  std_devs = data.frame(
    t = liver$t,
    Signal_HU = liver$hu_std,
    Signal_Kedge = liver$gd_std
  )
)

spleen_stats_adjusted <- list(
  averages = data.frame(
    t = spleen_stats$averages$t,
    Signal_HU = spleen_stats$averages$Signal_HU,
    Signal_Kedge = spleen_stats$averages$Signal_Kedge,
    Noise_HU = rep(NA, nrow(spleen_stats$averages)),  # Placeholder if needed
    Noise_Kedge = rep(NA, nrow(spleen_stats$averages)),  # Placeholder if needed
    CNR_HU = rep(NA, nrow(spleen_stats$averages)),  # Placeholder if needed
    CNR_Kedge = rep(NA, nrow(spleen_stats$averages))  # Placeholder if needed
  ),
  std_devs = data.frame(
    t = spleen_stats$std_devs$t,
    Signal_HU = spleen_stats$std_devs$Signal_HU,
    Signal_Kedge = spleen_stats$std_devs$Signal_Kedge,
    Noise_HU = rep(NA, nrow(spleen_stats$std_devs)),  # Placeholder if needed
    Noise_Kedge = rep(NA, nrow(spleen_stats$std_devs)),  # Placeholder if needed
    CNR_HU = rep(NA, nrow(spleen_stats$std_devs)),  # Placeholder if needed
    CNR_Kedge = rep(NA, nrow(spleen_stats$std_devs))  # Placeholder if needed
  )
)

liver_stats_adjusted <- list(
  averages = data.frame(
    t = liver_stats$averages$t,
    Signal_HU = liver_stats$averages$Signal_HU,
    Signal_Kedge = liver_stats$averages$Signal_Kedge,
    Noise_HU = rep(NA, nrow(liver_stats$averages)),  # Placeholder if needed
    Noise_Kedge = rep(NA, nrow(liver_stats$averages)),  # Placeholder if needed
    CNR_HU = rep(NA, nrow(liver_stats$averages)),  # Placeholder if needed
    CNR_Kedge = rep(NA, nrow(liver_stats$averages))  # Placeholder if needed
  ),
  std_devs = data.frame(
    t = liver_stats$std_devs$t,
    Signal_HU = liver_stats$std_devs$Signal_HU,
    Signal_Kedge = liver_stats$std_devs$Signal_Kedge,
    Noise_HU = rep(NA, nrow(liver_stats$std_devs)),  # Placeholder if needed
    Noise_Kedge = rep(NA, nrow(liver_stats$std_devs)),  # Placeholder if needed
    CNR_HU = rep(NA, nrow(liver_stats$std_devs)),  # Placeholder if needed
    CNR_Kedge = rep(NA, nrow(liver_stats$std_devs))  # Placeholder if needed
  )
)

library(ggplot2)


library(ggplot2)

plotOrganDataBars <- function(data_list, title, ylab, y_breaks, type) {
  # Prepare the time points; ensure these match your actual time points
  time_points <- c(0.11, 0.5, 1, 3, 10)
  
  # Create the plot data by combining all organ data frames and adding an 'Organ' column
  plot_data <- do.call(rbind, lapply(names(data_list), function(org) {
    df <- data_list[[org]]
    df$Organ <- org
    transform(df, TimePoint = factor(t, levels = as.character(time_points)))
  }))
  
  # Determine the columns to plot based on 'type'
  signal <- ifelse(type == "Gd", "gd", "hu")
  std <- ifelse(type == "Gd", "gd_std", "hu_std")
  
  # Create the plot
  gg <- ggplot(plot_data, aes_string(x = "TimePoint", y = signal, fill = "Organ")) +
    geom_bar(stat = "identity", position = position_dodge(width = 0.7), width = 0.6) +
    geom_errorbar(aes_string(ymin = paste(signal, "-", std), ymax = paste(signal, "+", std)), 
                  width = 0.2, position = position_dodge(width = 0.7)) +
    scale_fill_manual(values = c("Spleen" = "hotpink", "Liver" = "gold")) +
    labs(title = title, x = "Time (min)", y = ylab) +
    scale_y_continuous(expand = expansion(mult = c(0.003, 0.006)), breaks = y_breaks) +
    theme_minimal() +
    theme(
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      plot.title = element_text(hjust = 0.5, size = 30), 
      legend.title = element_blank(), 
      axis.line = element_line(color="black", linewidth = 1),
      axis.ticks = element_line(color = "black"),
      axis.title = element_text(size = 30),
      panel.border = element_blank(),
      axis.title.y = element_text(size = 30, margin = margin(r = 20)),
      axis.title.x = element_text(size = 30, margin = margin(t = 20)),
      panel.background = element_rect(fill = "white"), 
      axis.text.x = element_text(size = 30),
      axis.text = element_text(size = 30, margin = margin(r = 20), face = "bold")
    )
  
  # Print the plot
  print(gg)
}

# Example usage
plotOrganDataBars(
  data_list = list(Pancreas = pancreas, Spleen = spleen, Liver = liver),
  title = "Gd K-edge Organ Enhancement",
  ylab = "[Gd] (mg/mL)",
  y_breaks = seq(0, 2, by = 0.3),  # Adjust y_breaks according to the actual range of your data
  type = "Gd"
)

# Example usage
plotOrganDataBars(
  data_list = list(Pancreas = pancreas, Spleen = spleen, Liver = liver),
  title = "Conventional Organ Enhancement",
  ylab = "Hounsfield Units (HU)",
  y_breaks = seq(-500, 500, by = 50),  # Adjust y_breaks according to the actual range of your data
  type = "HU"
)
