library(ggplot2)
library(tidyr)
library(dplyr)

# Given your data setup
time_points <- c(0.11, 0.5, 1, 3, 10)

# Add significance values directly into the data frames
IVC_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX = c(0.866579641,
            1.169944183,
            1.099720557,
            0.958772503,
            0.770422062
  ),
  Dotarem = c(0.48632988,
              0.863424643,
              0.812724906,
              0.70351951,
              0.558018933
  ),
  Sig1 = c(0.2802, 0.01074, 0.02637, 0.02916, 0.02726)
)

Aorta_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX = c(3.562224594,
            1.121731011,
            1.049143745,
            0.893461014,
            0.737940953
  ),
  Dotarem = c(3.651371607,
              0.824053479,
              0.840478556,
              0.709781042,
              0.618284264
  ),
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
  labs(x = "Time (min)", y = "[Gd] (mg/mL)") +
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
  scale_y_continuous(expand = expansion(mult = c(0, 0.05)), limits = function(x) c(0, max(x) + 1)) +
  geom_vline(xintercept = c(2.5, 4.5), linetype = "dotted", color = "black") +
  geom_text(data = filter(combined_data, Sig < 0.05), aes(label = "*", group = Agent), position = position_dodge(width = 0.7), vjust = 0.05, color = "black") +
  geom_text(data = filter(combined_data, Sig < 0.01), aes(label = "**", group = Agent), position = position_dodge(width = 0.7), vjust = 0.05, color = "black") +
  geom_text(data = filter(combined_data, Sig < 0.001), aes(label = "***", group = Agent), position = position_dodge(width = 0.7), vjust = 0.05, color = "black") +
  # Global significance for IVC only
  geom_text(data = filter(combined_data, Location == "Inferior Vena Cava"), aes(x = Inf, y = Inf, label = "Global p < 0.0005***"), vjust = 1, hjust = 1.75, color = "red", size = 6)

print(gg)
