rm(list=ls())

library(sn)
library(stats4)

#dataFile <- '/scr/rain2/rsfdata/projects/pecan/zdr_in_ice/qcv3/rhi/ZdrmInIce_june.txt'
s=dataFile <- '/scr/rain1/rsfdata/projects/dynamo/zdr_in_ice/qcv2/rhi/ZdrmInIce.nov.txt'
#Read elevation and zdr data
elevZdr <- read.table(dataFile)

par(mfrow=c(2,1))
histZdr <- hist(elevZdr[,1],breaks=40,freq=FALSE, xlab = "ZDR", ylab = "Frequency", main='Dynamo November, histogram')

#olo.ph <- wines[wines$wine=="Barolo", "phenols"]
fit <- selm(elevZdr[,1] ~ 1, family="SN", xlab = "ZDR", ylab = "Frequency", xlim=c(-0.2,1.2),main='Dynamo November, skewed normal fit')
plot(fit, which=2)

#dev.copy2pdf(file = paste('/h/eol/romatsch/nex-Spol/figs/ZDRice/skewedNormal_dynamoNovember.pdf',sep=""))