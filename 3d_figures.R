library(ggplot2)
library(tidyr)

# Data setup
time_points <- c(0.11, 0.5, 1, 3, 10)

# Create data frames for each contrast agent and location
IVC_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX = c(65.65292385, 95.21815666, 90.99524308, 86.05621299, 72.05134089),
  Dotarem = c(53.11232372, 71.47004478, 70.66806427, 63.94803504, 54.67438008)
)

Aorta_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX = c(360.335973, 95.71676383, 90.51265177, 81.23382611, 67.57734131),
  Dotarem = c(259.5443653, 72.32383408, 72.46993674, 63.16742201, 56.91113616)
)

# Reshape data for plotting
IVC_long <- pivot_longer(IVC_data, cols = c(AGuIX, Dotarem), names_to = "Agent", values_to = "Signal")
Aorta_long <- pivot_longer(Aorta_data, cols = c(AGuIX, Dotarem), names_to = "Agent", values_to = "Signal")

# Combine datasets
combined_data <- bind_rows(IVC_long, Aorta_long)
combined_data$Location <- rep(c("IVC", "Aorta"), each = 10)

# Define aesthetic elements for consistency
font_family <- "Helvetica"
font_size_title <- 30  # Set title size larger for emphasis
font_size_axis_title <- 30  # Axis titles
font_size_text <- 30  # Text for axis ticks and legend
font_size_facet <- 30  # Facet strip text size

# Plot
gg <- ggplot(combined_data, aes(x = Time, y = Signal, fill = Agent)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.7), width = 0.6) +
  scale_fill_manual(values = c("AGuIX" = "lightblue", "Dotarem" = "gold")) +
  facet_wrap(~Location, scales = "free_y") +
  labs(
       x = "Time (min)", y = "Signal Intensity (HU)") +
  theme_minimal() +
  theme(
    text = element_text(family = font_family),
    plot.title = element_text(size = font_size_title, face = "bold", hjust = 0.5),
    axis.title = element_text(size = font_size_axis_title),
    axis.text = element_text(size = font_size_text),
    axis.text.x = element_text(angle = 45, hjust = 1),
    legend.title = element_blank(),
    legend.text = element_text(size = font_size_text),panel.grid.major = element_blank(),panel.grid.minor = element_blank(),
    strip.text = element_text(size = font_size_facet, face = "bold"),axis.line = element_line(color = "black", size = 1)    # Adjusting facet header size
  )+
  scale_y_continuous(expand = expansion(mult = c(0, 0.05)), limits = function(x) c(0, max(x) + 10)) +
  geom_vline(xintercept = c(2.5, 4.5), linetype = "dotted", color = "black") # Vertical dotted lines

# Print the plot
print(gg)
