# Define the corrected data without timepoint 1
if (!require(plotrix)) install.packages("plotrix")
library(plotrix)

library(tidyverse)
time_points <- c(0.11, 0.5, 1, 3, 10)

library(tidyverse)

time_points <- c(0.11, 
  0.5, 1, 3, 10)

# Integrate error values directly into the IVC data frame
IVC_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX_Signal = c(0.404020372,
                   0.633491497,
                   0.529428123,
                   0.392791825,
                   0.193267958
  ),
  AGuIX_Error = c(1.160021844,
                  0.301178064,
                  0.243577047,
                  0.15216335,
                  0.107964554
  ),
  Dotarem_Signal = c(-0.072873211,
                     0.282741205,
                     0.233440081,
                     0.127247248,
                     -0.01423952
  ),
  Dotarem_Error = c(1.375487634,
                    0.300920081,
                    0.235936007,
                    0.396024231,
                    0.52192442
  ),
  Sig1 = c( 0.2802, 
    0.01074, 0.02637, 0.02916, 0.02726)
)




# Integrate error values directly into the Aorta data frame
Aorta_data <- data.frame(
  Time = factor(time_points, levels = time_points),
  AGuIX_Signal = c(
    5.548945201,
    0.619190801,
    0.536298914,
    0.353784247,
    0.203349585
    
  ),
  AGuIX_Error = c(
    2.668772468,
    0.293979527,
    0.255942515,
    0.166786245,
    0.110971092
    
  ),
  Dotarem_Signal = c(
    4.889087292,
    0.189889576,
    0.217189187,
    -3.90965E-05,
    -0.152113051
  ),
  Dotarem_Error = c(
    1.9160746,
    0.227797662,
    0.180582761,
    0.138080988,
    0.127020902
    
  )
 ,
  Sig2 = c( 0.9875, 
    0.007302, 0.0387, 0.02073, 0.06486)
)




# Define aesthetic elements for consistency
font_family <- "Helvetica"
font_size_title <- 45
font_size_axis_title <- 35
font_size_text <- 35
font_size_facet <- 45

# For IVC data
IVC_long <- IVC_data %>%
  pivot_longer(
    cols = c(AGuIX_Signal, AGuIX_Error, Dotarem_Signal, Dotarem_Error),
    names_to = c("Agent", ".value"), # This determines how the names are assigned to new columns
    names_pattern = "(.*)_(.*)"
  )

# For Aorta data
Aorta_long <- Aorta_data %>%
  pivot_longer(
    cols = c(AGuIX_Signal, AGuIX_Error, Dotarem_Signal, Dotarem_Error),
    names_to = c("Agent", ".value"), # Same as above for consistency
    names_pattern = "(.*)_(.*)"
  )



# Combine the IVC and Aorta datasets
combined_data <- bind_rows(
  IVC_long %>% mutate(Location = "Inferior Vena Cava"),
  Aorta_long %>% mutate(Location = "Abdominal Aorta")
)


# Plot
gg <- ggplot(combined_data, aes(x = Time, y = Signal, fill = Agent)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.7), width = 0.6) +
  geom_errorbar(aes(ymin = pmax(Signal - Error, 0.0), ymax = Signal + Error), width = 0.2, position = position_dodge(width = 0.7)) +
  scale_fill_manual(values = c("AGuIX" = "lightblue", "Dotarem" = "gold")) +
  facet_wrap(~Location, scales = "free_y") +
  labs(x = "Time (min)", y = "[Gd] (mg/mL)") +
  theme_minimal() +
  theme(
    text = element_text(family = font_family),
    plot.title = element_text(size = font_size_title, face = "bold", hjust = 0.5),
    axis.title = element_text(size = font_size_axis_title),
    axis.title.y = element_text(size = font_size_axis_title, vjust = 1.0),
    axis.text = element_text(size = font_size_text),
    axis.text.x = element_text(vjust = 0.15),
    axis.text.y = element_text(hjust = 0.15),
    legend.title = element_blank(),
    legend.text = element_text(size = 35),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    strip.text = element_text(size = font_size_facet, face = "bold"),
    axis.line = element_line(color = "black", size = 1)
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.05)), limits = function(x) c(0, 8.5)) +
  geom_vline(xintercept = c(2.5, 4.5), linetype = "dotted", color = "black") +
  geom_text(data = filter(combined_data, Location == "Inferior Vena Cava"), aes(x = Inf, y = Inf, label = "Global p < 0.01**"), vjust = 1.45, hjust = 2.2, color = "red", size = 12) + 
  geom_hline(yintercept = 0.2, linetype = "dotted", color = "black", size = 1.5)
  
print(gg)


ggsave("output_plot.png", plot = gg, width = 9000, height = 2500, units = "px")
