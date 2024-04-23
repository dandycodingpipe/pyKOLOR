#Kidney
print(wilcox.test(aguix_cortex_stats$averages$Signal_HU, dotarem_cortex_stats$averages$Signal_HU, paired = TRUE))
print(wilcox.test(aguix_medulla_stats$averages$Signal_HU, dotarem_medulla_stats$averages$Signal_HU, paired = TRUE))
print(wilcox.test(aguix_pelvis_stats$averages$Signal_HU, dotarem_pelvis_stats$averages$Signal_HU, paired = TRUE))



#Vessels
n = 5
dotarem_hu_values <- unlist(sapply(dotarem_IRVC_data, function(x) x[n, "Signal_HU"]))
print(dotarem_hu_values)

aguix_hu_values <- unlist(sapply(aguix_IRVC_data, function(x) x[n, "Signal_HU"]))
print(aguix_hu_values)

print(wilcox.test(dotarem_hu_values, aguix_hu_values, paired = TRUE))

# PAIRED T-TEST (ASSUMPTION OF NORMALIT)
shapiro.test(dotarem_hu_values - aguix_hu_values)
plot(dotarem_hu_values)
plot(aguix_hu_values)
t.test(dotarem_hu_values, aguix_hu_values, paired = TRUE)

# Global Significance
print(wilcox.test(aguix_IRVC_stats$averages$Signal_HU, dotarem_IRVC_stats$averages$Signal_HU, paired = TRUE))
shapiro.test(aguix_IRVC_stats$averages$Signal_HU - dotarem_IRVC_stats$averages$Signal_HU)
print(t.test(aguix_IRVC_stats$averages$Signal_HU , dotarem_IRVC_stats$averages$Signal_HU ,paired = TRUE))


#Kidneys
n = 5
dotarem_hu_values <- unlist(sapply(dotarem_pelvis_data, function(x) x[n, "Signal_HU"]))
aguix_hu_values <- unlist(sapply(aguix_pelvis_data, function(x) x[n, "Signal_HU"]))
print(wilcox.test(dotarem_hu_values, aguix_hu_values, paired = TRUE))

# PAIRED T-TEST (ASSUMPTION OF NORMALIT)
shapiro.test(dotarem_hu_values - aguix_hu_values)
plot(dotarem_hu_values)
plot(aguix_hu_values)
t.test(dotarem_hu_values, aguix_hu_values, paired = TRUE)

# Global Significance
print(wilcox.test(aguix_pelvis_stats$averages$Signal_HU, dotarem_pelvis_stats$averages$Signal_HU, paired = TRUE))
shapiro.test(aguix_pelvis_stats$averages$Signal_HU - dotarem_pelvis_stats$averages$Signal_HU)
print(t.test(aguix_pelvis_stats$averages$Signal_HU , dotarem_pelvis_stats$averages$Signal_HU ,paired = TRUE))

