template_df = data.frame("t" = c(0.11, 0.5, 1, 3, 10), "hu" = c(1:5), "hu_std" = c(1:5), "gd" = c(1:5), "gd_std"= c(1:5))

pancreas = template_df
pancreas$hu = c(131.375,133.163915,110.909382,94.09557749,82.38494152)
pancreas$hu_std = c(45.94387104,
                 23.96608403,
                 16.95423335,
                 21.02401168,
                 16.65508335
)

pancreas$gd = c(0.92275,
                0.669025063,
                0.436896094,
                0.188815163,
                0.092470029
)
pancreas$gd_std = c(0.63442094,
                    0.311938844,
                    0.185376573,
                    0.094274716,
                    0.089290014
)

spleen = template_df

spleen$hu = c(151.125,
              125.4436247,
              106.8411915,
              86.17297932,
              80.52978279
)
spleen$hu_std = c(52.2779317,
                  19.89121772,
                  14.4636795,
                  18.28916974,
                  9.606424392
)
  
spleen$gd = c(1.149625,
              0.604440191,
              0.406629689,
              0.238968577,
              0.060972065
)
spleen$gd_std = c(0.868760519,
                  0.268049181,
                  0.17600373,
                  0.23628505,
                  0.070839551
)
  

liver = template_df
liver$hu = c(74.58157895,
             98.52055138,
             94.4414787,
             90.80153956,
             79.63147154
)
liver$hu_std = c(7.846929665,
                 12.87711238,
                 11.14391487,
                 10.39415688,
                 11.94766289
)
liver$gd = c(0,
             0.328953455,
             0.30053276,
             0.203143931,
             0.050097744
)
liver$gd_std = c(0,
                 0.160024207,
                 0.165976941,
                 0.125296811,
                 0.062815978
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
    scale_fill_manual(values = c("Pancreas" = "cyan", "Spleen" = "hotpink", "Liver" = "gold")) +
    labs(title = title, x = "Time (min)", y = ylab) +
    scale_y_continuous(expand = expansion(mult = c(0.003, 0.006)), breaks = y_breaks) +
    theme_minimal() +
    theme(
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      plot.title = element_text(hjust = 0.5, size = 24), 
      legend.title = element_blank(), 
      axis.line = element_line(color="black", linewidth = 1),
      axis.ticks = element_line(color = "black"),
      axis.title = element_text(size = 32),
      panel.border = element_blank(),
      axis.title.y = element_text(size = 24, margin = margin(r = 20)),
      axis.title.x = element_text(size = 24, margin = margin(t = 20)),
      panel.background = element_rect(fill = "white"), 
      axis.text.x = element_text(size = 24),
      axis.text = element_text(size = 24, margin = margin(r = 20), face = "bold")
    )
  
  # Print the plot
  print(gg)
}

# Example usage
plotOrganDataBars(
  data_list = list(Pancreas = pancreas, Spleen = spleen, Liver = liver),
  title = "Gd K-edge Organ Enhancement",
  ylab = "[Gd] (mg/mL)",
  y_breaks = seq(0, 2, by = 0.2),  # Adjust y_breaks according to the actual range of your data
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
