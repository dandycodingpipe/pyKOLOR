# Assuming cortex_stats, medulla_stats, pelvis_stats, cort_d, med_d, and pelv_d are defined and the necessary libraries are loaded.

# Prepare Data
a_mc_diff <- medulla_stats$averages$Signal_HU[-1] - cortex_stats$averages$Signal_HU[-1]
a_rm_diff <- pelvis_stats$averages$Signal_HU[-1] - medulla_stats$averages$Signal_HU[-1]

d_mc_diff <- med_d$Signal_HU[-1] - cort_d$Signal_HU[-1]
d_rm_diff <- pelv_d$Signal_HU[-1] - med_d$Signal_HU[-1]

aguix <- aguix_cortex_stats$averages$Signal_HU
dotarem <- dotarem_cortex_stats$averages$Signal_HU

# Create a data frame for plotting intra-renal feature contrast differences
data_diff <- data.frame(
  Timepoint = factor(rep(c("0.5", "1", "3", "10"), 4), levels = c("0.5", "1", "3", "10")),
  Difference = c(aguix, dotarem),
  Comparison = factor(rep(c("AGuIX", "Dotarem"), each = 4))
)

# Create the bar plot
# Continue with the adjusted ggplot code
ggplot(data_diff, aes(x = Timepoint, y = Difference, fill = Comparison)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.8), width = 0.6) +
  labs(x = "Time (min)", y = expression(Delta * " Signal HU"), title = "Difference in Signal Between Pelvis & Medulla") +
  theme_minimal() +
  # Customize the colors manually for each comparison group
  scale_fill_manual(values = c("AGuIX" = "darkgreen", "Dotarem" = "lightgreen")) +
  theme(
    plot.title = element_text(hjust = 0.5, size = 24),
    legend.title = element_blank(),
    axis.line = element_line(color="black", size = 1),
    axis.title = element_text(size = 32),
    axis.text = element_text(size = 24),
    panel.background = element_rect(fill = "white"),
    panel.grid.major = element_blank(),  # Remove major grid lines
    panel.grid.minor = element_blank()   # Remove minor grid lines
  ) +
  # Adjust y-axis ticks: specify the range and intervals of ticks
  scale_y_continuous(breaks = seq(from = -50, to = 200, by = 20))





data_diff <- data.frame(
  Timepoint = factor(rep(c("0.5", "1", "3", "10"), 4), levels = c("0.5", "1", "3", "10")),
  Difference = c(a_mc_diff, d_mc_diff),
  Comparison = factor(rep(c("AGuIX", "Dotarem"), each = 4))
)

# Continue with the adjusted ggplot code
ggplot(data_diff, aes(x = Timepoint, y = Difference, fill = Comparison)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.8), width = 0.6) +
  labs(x = "Time (min)", y = expression(Delta * " Signal HU"), title = "Difference in Signal Between Medulla & Cortex") +
  theme_minimal() +
  # Customize the colors manually for each comparison group
  scale_fill_manual(values = c("AGuIX" = "darkblue", "Dotarem" = "lightblue")) +
  theme(
    plot.title = element_text(hjust = 0.5, size = 24),
    legend.title = element_blank(),
    axis.line = element_line(color="black", size = 1),
    axis.title = element_text(size = 32),
    axis.text = element_text(size = 24),
    panel.background = element_rect(fill = "white"),
    panel.grid.major = element_blank(),  # Remove major grid lines
    panel.grid.minor = element_blank()   # Remove minor grid lines
  ) +
  # Adjust y-axis ticks: specify the range and intervals of ticks
  scale_y_continuous(breaks = seq(from = -50 , to = max(data_diff$Difference) + 10, by = 10))


