library(ggplot2)
library(grid)

# Define categories and their corresponding unique colors
categories <- c("Suprarenal abdominal aorta", "Infrarenal aorta", "Inferior vena cava", "Infrarenal vena cava" ,"Cortex","Medulla", "Pelvis", "Liver" ,"Spleen")
colors <- c("Suprarenal abdominal aorta" = "red", 
            "Infrarenal aorta" = "pink",  
            "Inferior vena cava" = "blue", 
            "Infrarenal vena cava" = "lightblue", 
            "Cortex" = "purple", 
            "Medulla" = "orange",  
            "Pelvis" = "lightgreen",
            "Liver" = "gold",
            "Spleen"=  "hotpink")

# Create a dummy dataframe
data <- data.frame(Category = factor(categories, levels = categories))

# Create the plot with proper color mappings
gg <- ggplot(data, aes(x = 1, y = Category, fill = Category)) +
  geom_tile() +  # using geom_tile to create colored boxes
  scale_fill_manual(values = colors) +
  theme_void() +
  theme(legend.position = "bottom", 
        legend.text = element_text(size = 12, face = "bold"),  # Bold legend text
        legend.box.spacing = unit(2, "lines"),  # Increase spacing between legend items
        legend.spacing.x = unit(1, "cm"),  # Increase spacing between legend columns
        legend.spacing.y = unit(1, "cm")) +  # Increase spacing between legend rows
  guides(fill = guide_legend(title = "", 
                             nrow = 3, ncol = 3,  # Specify the layout of the legend items
                             byrow = TRUE))  # Fill by rows first

# Extract the legend
g <- ggplotGrob(gg)
legend <- gtable::gtable_filter(g, "guide-box")

# Draw the legend
grid.newpage()
grid.draw(legend)

