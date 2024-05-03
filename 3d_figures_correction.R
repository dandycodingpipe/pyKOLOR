library(ggplot2)
library(tidyr)
library(dplyr)

# Given your data setup
time_points <- c( 0.5, 1, 3, 10)

# Add significance values directly into the data frames
IVC_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX = c(
            0.572193647,
            0.516482852,
            0.366400906,
            0.2103856
  ),
  Dotarem = c(
              0.265211749,
              0.219756813,
              0.121848526,
              0
              
  ),
  Sig1 = c( 0.01074, 0.02637, 0.02916, 0.02726)
)

Aorta_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX = c(
            0.563418086,
            0.485002754,
            0.324007433,
            0.220293914
            
  ),
  Dotarem = c(
              0.243680181,
              0.264069932,
              0.101824741,
              -0.011757466
              
  ),
  Sig2 = c(0.007302, 0.0387, 0.02073, 0.06486)
)

# Reshape data for plotting and include Sig as part of the long data
IVC_long <- pivot_longer(IVC_data, cols = c(AGuIX, Dotarem), names_to = "Agent", values_to = "Signal") %>%
  mutate(Sig = ifelse(Agent == "AGuIX", Sig1, Sig1))

Aorta_long <- pivot_longer(Aorta_data, cols = c(AGuIX, Dotarem), names_to = "Agent", values_to = "Signal") %>%
  mutate(Sig = ifelse(Agent == "AGuIX", Sig2, Sig2))

# Combine datasets
combined_data <- bind_rows(IVC_long, Aorta_long) %>%
  mutate(Location = rep(c("Inferior Vena Cava", "Abdominal Aorta"), each = 8))

# Define aesthetic elements for consistency
font_family <- "Helvetica"
font_size_title <- 45
font_size_axis_title <- 35
font_size_text <- 35
font_size_facet <- 45

gg <- ggplot(combined_data, aes(x = Time, y = Signal, fill = Agent)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.7), width = 0.6) +
  scale_fill_manual(values = c("AGuIX" = "lightblue", "Dotarem" = "gold")) +
  facet_wrap(~Location, scales = "free_y") +
  labs(x = "Time (min)", y = "[Gd] (mg/mL)") +
  theme_minimal() +
  theme(
    text = element_text(family = font_family),
    plot.title = element_text(size = font_size_title, face = "bold", hjust = 0.5),
    axis.title.x = element_text(size = font_size_axis_title, margin = margin(t=15)),
    axis.title.y = element_text(size = font_size_axis_title, margin = margin(r=15)),
    axis.text = element_text(size = font_size_text),
    axis.text.y = element_text(hjust = -1, margin = margin(r = 10)),  # Adjust the right margin (r)
    axis.text.x = element_text(hjust = 1, vjust = 1, margin = margin(t = 10)),  # Adjust the top margin (t)
    legend.title = element_blank(),
    legend.text = element_text(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    strip.text = element_text(size = font_size_facet, face = "bold"),
    axis.line = element_line(color = "black", size = 1)
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.05)), limits = function(x) c(0, 1)) +
  geom_vline(xintercept = c(2.5, 4.5), linetype = "dotted", color = "black") +
  geom_text(data = filter(combined_data, Sig < 0.05 & Sig >= 0.01), aes(label = "*", group = Agent), position = position_dodge(width = 0.7), vjust = -0.5, color = "black", size = 20) +
  geom_text(data = filter(combined_data, Sig < 0.01 & Sig >= 0.001), aes(label = "**", group = Agent), position = position_dodge(width = 0.7), vjust = -0.5, color = "black", size = 20) +
  geom_text(data = filter(combined_data, Sig < 0.001), aes(label = "***", group = Agent), position = position_dodge(width = 0.7), vjust = -0.5, color = "red", size = 16) +
  geom_text(data = filter(combined_data, Location == "Inferior Vena Cava"), aes(x = Inf, y = Inf, label = "Global p < 0.01**"), vjust = 1.45, hjust = 1.65, color = "red", size = 12)

print(gg)
# Save the plot with specified dimensions
ggsave("output_plot.png", plot = gg, width = 7500, height = 2500, units = "px")

