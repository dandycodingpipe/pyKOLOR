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


#3D Vessels

#Global 


 meanAGuIX <- c(2341.3125,
                2752.1875,
                2752.1875,
                2752.1875,
                2748.375
                
 )
 
 stdAGuIX <- c(2029.020833,
               2029.020833,
               2029.020833,
               2029.020833,
               2118.95
               
               
               
 )
 
  meanDotarem <- c(2723.979167,
                   2815.3125,
                   2723.979167,
                   2723.979167,
                   2857.75
                   
                   
  )
 
   stdDotarem <- c(2074.4375,
                   2055.75,
                   2074.4375,
                   2074.4375,
                   2210.8
                   
                   
                   
                   
)

print(shapiro.test(meanAGuIX - meanDotarem))
print(shapiro.test(stdAGuIX - stdDotarem))

print(t.test(meanAGuIX, meanDotarem, paired = TRUE))
print(t.test(stdAGuIX, stdDotarem, paired = TRUE))
print(wilcox.test(stdAGuIX, stdDotarem, paired = TRUE))
