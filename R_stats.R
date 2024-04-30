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


 meanAGuIX <- c(0.866579641,
                1.169944183,
                1.099720557,
                0.958772503,
                0.770422062
                
                
 )
 
 stdAGuIX <- c(0.558441541,
               0.155536453,
               0.124091693,
               0.071656162,
               0.097006985
           
 )
 
  meanDotarem <- c(0.48632988,
                   0.863424643,
                   0.812724906,
                   0.70351951,
                   0.558018933
                   
                   
  )
 
   stdDotarem <- c(0.748274375,
                   0.169046512,
                   0.134017922,
                   0.220310831,
                   0.288175245
                   
                   
                   
                   
                   
)

print(shapiro.test(meanAGuIX - meanDotarem))
print(shapiro.test(stdAGuIX - stdDotarem))

print(t.test(meanAGuIX, meanDotarem, paired = TRUE))
print(t.test(stdAGuIX, stdDotarem, paired = TRUE))
print(wilcox.test(stdAGuIX, stdDotarem, paired = TRUE))
