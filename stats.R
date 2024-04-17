#Kidney
print(wilcox.test(aguix_cortex_stats$averages$Signal_HU, dotarem_cortex_stats$averages$Signal_HU, paired = TRUE))
print(wilcox.test(aguix_medulla_stats$averages$Signal_HU, dotarem_medulla_stats$averages$Signal_HU, paired = TRUE))
print(wilcox.test(aguix_pelvis_stats$averages$Signal_HU, dotarem_pelvis_stats$averages$Signal_HU, paired = TRUE))



#Vessels
print(wilcox.test(aguix_SAA_stats$averages$Signal_HU, dotarem_SAA_stats$averages$Signal_HU, paired = TRUE))

at1 = c(303.0841121,	572.3703704,	657.220339,	560.287234,	432.4764706)
at2 = c(114.8058252,	117.1222222,	123.9304348,	117.1521739,	102.9375)
at3 <- c(93.62135922,	108.2888889,	104.6086957,	122.1956522,	113.4)
at4 = c(94.72815534,	81.05555556,	101.1130435,	83.91304348,	86.46875)
at5 = c(87.50485437,	66.21111111,	68.00869565,	62.81521739,	72.40625)

dt1 = c(223.9565217, 333.6176471,	516.9433962,	408.8901099,	364.9259259)
dt2 = c(55.84057971,	95.18902439,	64.79245283,	94.70114943,	71.35185185)
dt3 = c(54.49275362,	94.38414634,	66.37735849,	85.80991736,	74.09259259)
dt4 = c(66.24637681,	78.81097561,	59.32075472,	67.28099174,	60.68518519)
dt5 = c(54.10144928,	73.12804878,	48.01886792, 57.19008264, 66.11881188)


#
ag = at5
do = dt5
plot(do)
print(wilcox.test(ag, do, paired = TRUE))
shapiro.test(ag - do)
t.test(ag, do, paired = TRUE)

#
shapiro.test(aguix_cortex_stats$averages$Signal_HU - dotarem_cortex_stats$averages$Signal_HU)
print(t.test(aguix_cortex_stats$averages$Signal_HU, dotarem_cortex_stats$averages$Signal_HU, paired = TRUE))

print(wilcox.test(aguix_IRA_stats$averages$Signal_HU, dotarem_IRA_stats$averages$Signal_HU, paired = TRUE))
print(wilcox.test(aguix_IVC_stats$averages$Signal_HU, dotarem_IVC_stats$averages$Signal_HU, paired = TRUE))
print(wilcox.test(aguix_IRVC_stats$averages$Signal_HU, dotarem_IRVC_stats$averages$Signal_HU, paired = TRUE))


# Global Significance
shapiro.test(aguix_pelvis_stats$averages$Signal_HU - dotarem_pelvis_stats$averages$Signal_HU)
print(t.test(aguix_pelvis_stats$averages$Signal_HU , dotarem_pelvis_stats$averages$Signal_HU ,paired = TRUE))
