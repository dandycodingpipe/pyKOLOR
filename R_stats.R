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


 meanAGuIX <- c(
   5.548945201,
   0.619190801,
   0.536298914,
   0.353784247,
   0.203349585
   
 )
 
 stdAGuIX <- c(
   2.668772468,
   0.293979527,
   0.255942515,
   0.166786245,
   0.110971092
   
 )
 
  meanDotarem <- c(
    4.889087292,
    0.189889576,
    0.217189187,
    -3.90965E-05,
    -0.152113051
    
    
  )
 
   stdDotarem <- c(
     1.9160746,
     0.227797662,
     0.180582761,
     0.138080988,
     0.127020902
     
)

print(shapiro.test(meanAGuIX - meanDotarem))
print(shapiro.test(stdAGuIX - stdDotarem))

print(t.test(meanAGuIX, meanDotarem, paired = TRUE))
print(t.test(stdAGuIX, stdDotarem, paired = TRUE))
print(wilcox.test(meanAGuIX, meanDotarem, paired = TRUE))


print(shapiro.test(IRVC_stats$averages$CNR_Kedge - IRVC_stats$averages$CNR_HU))
t.test(IRVC_stats$averages$CNR_Kedge, IRVC_stats$averages$CNR_HU, paired = TRUE)
