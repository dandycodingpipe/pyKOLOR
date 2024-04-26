library(ggplot2)
library(tidyr)
library(dplyr)

# Given your data setup
time_points <- c(0.11, 0.5, 1, 3, 10)

# Add significance values directly into the data frames
IVC_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX = c(74.42618212, 95.34787468, 90.50486602, 80.78431054, 67.79462498),
  Dotarem = c(48.2020607, 74.2085961, 70.71206251, 63.18065587, 53.14613331),
  Sig1 = c(0.2802, 0.01074, 0.02637, 0.02916, 0.02726)
)

Aorta_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX = c(260.3327306, 92.02282838, 87.01680997, 76.28006995, 65.55454846),
  Dotarem = c(266.4808005, 71.49334339, 72.62610733, 63.61248562, 57.30236301),
  Sig2 = c(0.9875, 0.007302, 0.0387, 0.02073, 0.06486)
)

# Reshape data for plotting and include Sig as part of the long data
IVC_long <- pivot_longer(IVC_data, cols = c(AGuIX, Dotarem), names_to = "Agent", values_to = "Signal") %>%
  mutate(Sig = ifelse(Agent == "AGuIX", Sig1, Sig1))  # Adjust this as needed

Aorta_long <- pivot_longer(Aorta_data, cols = c(AGuIX, Dotarem), names_to = "Agent", values_to = "Signal") %>%
  mutate(Sig = ifelse(Agent == "AGuIX", Sig2, Sig2))  # Adjust this as needed

# Combine datasets
combined_data <- bind_rows(IVC_long, Aorta_long) %>%
  mutate(Location = rep(c("Inferior Vena Cava", "Abdominal Aorta"), each = 10))

# Proceed with plotting as previously described


# Define aesthetic elements for consistency
font_family <- "Helvetica"
font_size_title <- 30
font_size_axis_title <- 30
font_size_text <- 30
font_size_facet <- 30

gg <- ggplot(combined_data, aes(x = Time, y = Signal, fill = Agent)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.7), width = 0.6) +
  scale_fill_manual(values = c("AGuIX" = "lightblue", "Dotarem" = "gold")) +
  facet_wrap(~Location, scales = "free_y") +
  labs(x = "Time (min)", y = "Mean Blood Attenuation (HU)") +
  theme_minimal() +
  theme(
    text = element_text(family = font_family),
    plot.title = element_text(size = font_size_title, face = "bold", hjust = 0.5),
    axis.title = element_text(size = font_size_axis_title),
    axis.text = element_text(size = font_size_text),
    axis.text.x = element_text(angle = 45, hjust = 1),
    legend.title = element_blank(),
    legend.text = element_text(size = font_size_text),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    strip.text = element_text(size = font_size_facet, face = "bold"),
    axis.line = element_line(color = "black", size = 1)
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.05)), limits = function(x) c(0, max(x) + 10)) +
  geom_vline(xintercept = c(2.5, 4.5), linetype = "dotted", color = "black") +
  geom_text(data = filter(combined_data, Sig < 0.05), aes(label = "*", group = Agent), position = position_dodge(width = 0.7), vjust = 0.05, color = "black") +
  geom_text(data = filter(combined_data, Sig < 0.01), aes(label = "**", group = Agent), position = position_dodge(width = 0.7), vjust = 0.05, color = "black") +
  geom_text(data = filter(combined_data, Sig < 0.001), aes(label = "***", group = Agent), position = position_dodge(width = 0.7), vjust = 0.05, color = "black") +
  # Global significance for IVC only
  geom_text(data = filter(combined_data, Location == "Inferior Vena Cava"), aes(x = Inf, y = Inf, label = "Global p < 0.0005***"), vjust = 1, hjust = 1.75, color = "red", size = 6)

print(gg)
