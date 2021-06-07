library(tidyverse)

# Demographic.scv contains information on the age of the study participants, their gender, and familiarity with the area of the study
Demographics <- read_csv("Demographics.csv")
aggregate(Demographics[, 3], list(Demographics$Group), mean)
aggregate(Demographics[, 3], list(Demographics$Group), sd)
aggregate(Demographics[, 5], list(Demographics$Group), mean)
aggregate(Demographics[, 5], list(Demographics$Group), sd)

# SBSod_scored.csv includes the scored SBSoD Scale; reversed when necessary etc 
SBSoD_scored <- read_csv("SBSoD_scored.csv")
SBSoDGroup1<-SBSoD_scored[1:12, 1:17]
SBSoDGroup2<-SBSoD_scored[13:25, 1:17]
SBSoD1<-rowMeans(SBSoDGroup1[, 3:17])
SBSoD2<-rowMeans(SBSoDGroup2[, 3:17])
SBSoD1Desc<-data.frame(mean(SBSoD1), sd(SBSoD1))
SBSoD2Desc<-data.frame(mean(SBSoD2), sd(SBSoD2))
colnames(SBSoD1Desc) <- c("Mean", "SD")
colnames(SBSoD2Desc) <- c("Mean", "SD")
shapiro.test(SBSoD1)
shapiro.test(SBSoD2)
wilcox.test(SBSoD1, SBSoD2, exact = FALSE)

# The file MapErrors.csv contains information on three map sketching elements examined.
# It also includes the column "landmarks score" to account for the number of correctly added landmarks on map sketches
MapErrors <- read_csv("MapErrors.csv")
MapErrorsGroup1<-MapErrors[1:12, 1:7]
MapErrorsGroup2<-MapErrors[13:25, 1:7]
MapErrorsGroup1Desc<-data.frame(mean(MapErrorsGroup1$`landmarks omitted`), sd(MapErrorsGroup1$`landmarks omitted`), mean(MapErrorsGroup1$`road segments`), sd(MapErrorsGroup1$`road segments`), mean(MapErrorsGroup1$`total map errors`), sd(MapErrorsGroup1$`total map errors`), mean(MapErrorsGroup1$`landmarks score`), sd(MapErrorsGroup1$`landmarks score`))
colnames(MapErrorsGroup1Desc) <- c("MeanLandmarksOmitted", "SDLandmarksOmitted", "MeanRoadSegments", "SDRoadSegments", "MeanTotalMapErrors", "SDTotalMapErrors", "MeanLandmarksScore", "SDLandmarksScore")
MapErrorsGroup2Desc<-data.frame(mean(MapErrorsGroup2$`landmarks omitted`), sd(MapErrorsGroup2$`landmarks omitted`), mean(MapErrorsGroup2$`road segments`), sd(MapErrorsGroup2$`road segments`), mean(MapErrorsGroup2$`total map errors`), sd(MapErrorsGroup2$`total map errors`), mean(MapErrorsGroup2$`landmarks score`), sd(MapErrorsGroup2$`landmarks score`))
colnames(MapErrorsGroup2Desc) <- c("MeanLandmarksOmitted", "SDLandmarksOmitted", "MeanRoadSegments", "SDRoadSegments", "MeanTotalMapErrors", "SDTotalMapErrors", "MeanLandmarksScore", "SDLandmarksScore")
shapiro.test(MapErrorsGroup1$`total map errors`)
shapiro.test(MapErrorsGroup2$`total map errors`)
MapErrorsttest<-t.test(MapErrorsGroup1$`total map errors`, MapErrorsGroup2$`total map errors`)
shapiro.test(MapErrorsGroup1$`road segments`)
shapiro.test(MapErrorsGroup2$`road segments`)
Roadsegmentsttest<-t.test(MapErrorsGroup1$`road segments`, MapErrorsGroup2$`road segments`)
shapiro.test(MapErrorsGroup1$`landmarks omitted`)
shapiro.test(MapErrorsGroup2$`landmarks omitted`)
Landmarksomittedttest<-t.test(MapErrorsGroup1$`landmarks omitted`, MapErrorsGroup2$`landmarks omitted`)
shapiro.test(MapErrorsGroup1$`landmarks score`)
shapiro.test(MapErrorsGroup2$`landmarks score`)
LandmarksScorettest<-t.test(MapErrorsGroup1$`landmarks score`, MapErrorsGroup2$`landmarks score`)

#The workflow that follows performs statistical analysis for Directions Estimates
DirEstim <- read_csv("Directions.csv") # Directions.csv contains the participants' estimates on four directions
DirCorrect<-data.frame(0, 10, 270, 0) # The four values denote the correct directions that participants had to estimate
colnames(DirCorrect) <- c("Dir1", "Dir2", "Dir3", "Dir4")
DirScores<-data.frame(DirCorrect$Dir1-DirEstim$EST_DR1, DirCorrect$Dir2-DirEstim$EST_DR2, DirCorrect$Dir3-DirEstim$EST_DR3, DirCorrect$Dir4-DirEstim$EST_DR4)
colnames(DirScores) <- c("ScoreDir1", "ScoreDir2", "ScoreDir3", "ScoreDir4")
AbsDirScores<-data.frame(abs(DirScores))
AbsDirScores$ScoreDir2[18]=40 # Handling the estimation between 270o and 359o so that the score falls below 180o 
AAS <- rowMeans(AbsDirScores[,1:4]*100/180) # AAS: Absolute Accuracy Score
AASGroup1<-AAS[1:12]
AASGroup2<-AAS[13:25]
shapiro.test(AASGroup1)
shapiro.test(AASGroup2)
wilcox.test(AASGroup1, AASGroup2, exact = FALSE)
mean(AASGroup1)
sd(AASGroup1)
mean(AASGroup2)
sd(AASGroup2)
mean(DirScores$ScoreDir2)
mean(DirScores$ScoreDir3)

# The workflow that follows performs statistical analysis for Distances Estimates
DistEstim <- read_csv("Distances.csv") # Distances.csv contains the participants' estimates on four distances
DistCorrect<-data.frame(650, 60, 400, 55) # The values indicate the correct distances that participants had to estimate
colnames(DistCorrect) <- c("D1", "D2", "D3", "D4")
DistRelScores<-data.frame(DistEstim$ESTIM_D1-DistCorrect$D1, DistEstim$ESTIM_D2-DistCorrect$D2, DistEstim$ESTIM_D3-DistCorrect$D3, DistEstim$ESTIM_D4-DistCorrect$D4)
colnames(DistRelScores) <- c("RelScore1", "RelScore2", "RelScore3", "RelScore4")
DistAbScores<-data.frame(abs(DistRelScores))
colnames(DistAbScores) <- c("AbScore1", "AbScore2", "AbScore3", "AbScore4")
DistAbScores$TotalScore <- rowMeans(DistAbScores[,1:4]) # The total score in the distance estimation task is the average of the four distances estimates scores.  
DistAbScores<-DistAbScores[-c(3), ] # participant with p_id=3 is excluded from further analysis related to distance estimates
DistRelScores<-DistRelScores[-c(3), ]
DistAbScoreGroup1<-DistAbScores[1:11, 1:5]
DistAbScoreGroup2<-DistAbScores[12:24, 1:5]
DistAbScore1Desc<-data.frame(mean(DistAbScoreGroup1$AbScore1), sd(DistAbScoreGroup1$AbScore1), mean(DistAbScoreGroup1$AbScore2), sd(DistAbScoreGroup1$AbScore2), mean(DistAbScoreGroup1$AbScore3), sd(DistAbScoreGroup1$AbScore3), mean(DistAbScoreGroup1$AbScore4), sd(DistAbScoreGroup1$AbScore4), mean(DistAbScoreGroup1$TotalScore), sd(DistAbScoreGroup1$TotalScore))
colnames(DistAbScore1Desc) <- c("MeanScore1", "SDScore1", "MeanScore2","SDScore2", "MeanScore3", "SDScore3", "MeanScore4", "SDScore4", "MeanDistanceScore", "SDDistanceScore")
DistAbScore2Desc<-data.frame(mean(DistAbScoreGroup2$AbScore1), sd(DistAbScoreGroup2$AbScore1), mean(DistAbScoreGroup2$AbScore2), sd(DistAbScoreGroup2$AbScore2), mean(DistAbScoreGroup2$AbScore3), sd(DistAbScoreGroup2$AbScore3), mean(DistAbScoreGroup2$AbScore4), sd(DistAbScoreGroup2$AbScore4), mean(DistAbScoreGroup2$TotalScore), sd(DistAbScoreGroup2$TotalScore))
colnames(DistAbScore2Desc) <- c("MeanScore1", "SDScore1", "MeanScore2","SDScore2", "MeanScore3", "SDScore3", "MeanScore4", "SDScore4", "MeanDistanceScore", "SDDistanceScore")
shapiro.test(DistAbScoreGroup1$TotalScore)
shapiro.test(DistAbScoreGroup2$TotalScore)
Distancesttest<-t.test(DistAbScoreGroup1$TotalScore, DistAbScoreGroup2$TotalScore)

# Comparing between groups for each distance estimated; this script includes only the procedure for Distance #3
shapiro.test(DistAbScoreGroup1$AbScore3)
shapiro.test(DistAbScoreGroup2$AbScore3)

Distance3Comp<-wilcox.test(DistAbScoreGroup1$AbScore3, DistAbScoreGroup2$AbScore3, exact = FALSE)
#The process that follows consists of finding absolute and relative standard errors of distance estimates
meanAbsError<-data.frame(mean(DistAbScores$AbScore1/DistCorrect$D1*100), mean(DistAbScores$AbScore2/DistCorrect$D2*100), mean(DistAbScores$AbScore3/DistCorrect$D3*100), mean(DistAbScores$AbScore4/DistCorrect$D4*100))
colnames(meanAbsError) <- c("AbsEstError1", "AbsEstError2", "AbsEstError3", "AbsEstError4")
meanRelError<-data.frame(mean(DistRelScores$RelScore1/DistCorrect$D1*100), mean(DistRelScores$RelScore2/DistCorrect$D2*100), mean(DistRelScores$RelScore3/DistCorrect$D3*100), mean(DistRelScores$RelScore4/DistCorrect$D4*100))
colnames(meanRelError) <- c("RelEstError1", "RelEstError2", "RelEstError3", "RelEstError4")
seD1_absolute <- function() sqrt(var((DistAbScores$AbScore1/DistCorrect$D1)*100)/24) # finding standard errors for absolute and relative distance scores (in %)
print(seD1_absolute())
seD2_absolute <- function() sqrt(var((DistAbScores$AbScore2/DistCorrect$D2)*100)/24)
print(seD2_absolute())
seD3_absolute <- function() sqrt(var((DistAbScores$AbScore3/DistCorrect$D3)*100)/24)
seD4_absolute <- function() sqrt(var((DistAbScores$AbScore4/DistCorrect$D4)*100)/24)
seD1_relative <- function() sqrt(var((DistRelScores$RelScore1/DistCorrect$D1)*100)/24)
seD2_relative <- function() sqrt(var((DistRelScores$RelScore2/DistCorrect$D2)*100)/24)
seD3_relative <- function() sqrt(var((DistRelScores$RelScore3/DistCorrect$D3)*100)/24)
seD4_relative <- function() sqrt(var((DistRelScores$RelScore4/DistCorrect$D4)*100)/24)
seAbsolute<-c(seD1_absolute(), seD2_absolute(), seD3_absolute(), seD4_absolute())
seRelative<-c(seD1_relative(), seD2_relative(), seD3_relative(), seD4_relative())
seAbsolute<-round(seAbsolute,digits=2)
seRelative<-round(seRelative,digits=2)
meanRelativeErrors<-as.vector(t(meanRelError))
meanRelativeErrors<-round(meanRelativeErrors,digits=2)
meanAbsoluteErrors<-as.vector(t(meanAbsError))
meanAbsoluteErrors<-round(meanAbsoluteErrors,digits=2)
DistCorrect<-as.vector(t(DistCorrect))

# What follows creates the plot of the mean and standards error bars for both relative and absolute distance estimates
par(mar=c(4,4,1,1))
plot(DistCorrect, meanAbsoluteErrors, xlim= c(0, 700), ylim=c(-15, 50),xlab="Actual Distances", ylab="Absolute and real relative estimation error (%)", pch=16, cex=2, col="blue")
arrows(x0=DistCorrect, y0=meanAbsoluteErrors-seAbsolute, x1=DistCorrect, y1=meanAbsoluteErrors+seAbsolute, code=3, angle=90, length=0.1)
text(DistCorrect, y = meanAbsoluteErrors, labels = meanAbsoluteErrors, pos = 2, offset = 0.5, cex = 0.8, col = "blue")
par(new=TRUE)
plot(DistCorrect, meanRelativeErrors, xlim= c(0, 700), ylim=c(-15, 50),xlab="Actual Distances", ylab="Absolute and real relative estimation error (%)", pch=16, cex=2, col="red")
arrows(x0=DistCorrect, y0=meanRelativeErrors-seRelative, x1=DistCorrect, y1=meanRelativeErrors+seRelative, code=3, angle=90, length=0.1)
text(DistCorrect, y = meanRelativeErrors, labels = meanRelativeErrors, pos = 2, offset = 0.5, cex = 0.8, col = "red")

# Correlations calculations between variables follow

# Correlations between variables for Group 1
cor.test(SBSoD1, MapErrorsGroup1$`total map errors`, method="spearman", exact = FALSE)
cor.test(SBSoD1, MapErrorsGroup1$`landmarks omitted`, method="spearman", exact = FALSE)
cor.test(SBSoD1, MapErrorsGroup1$`road segments`, method="spearman", exact = FALSE)
cor.test(MapErrorsGroup1$`landmarks omitted`, MapErrorsGroup1$`road segments`, method="spearman", exact = FALSE)
cor.test(SBSoD1, AASGroup1, method="spearman", exact = FALSE)
cor.test(SBSoD1[-c(3)], DistAbScoreGroup1$TotalScore, method="spearman", exact = FALSE)
cor.test(MapErrorsGroup1$`total map errors`, AASGroup1, method="spearman", exact = FALSE)
cor.test(MapErrorsGroup1$`total map errors`[-c(3)], DistAbScoreGroup1$TotalScore, method="spearman", exact = FALSE)
cor.test(AASGroup1[-c(3)], DistAbScoreGroup1$TotalScore, method="spearman", exact = FALSE)

# Correlations between variables for Group 2
cor.test(SBSoD2, MapErrorsGroup2$`total map errors`, method="spearman", exact = FALSE)
cor.test(SBSoD2, MapErrorsGroup2$`landmarks omitted`, method="spearman", exact = FALSE)
cor.test(SBSoD2, MapErrorsGroup2$`road segments`, method="spearman", exact = FALSE)
cor.test(MapErrorsGroup2$`landmarks omitted`, MapErrorsGroup2$`road segments`, method="spearman", exact = FALSE)
cor.test(SBSoD2, AASGroup2, method="spearman", exact = FALSE)
cor.test(SBSoD2, DistAbScoreGroup2$TotalScore, method="spearman", exact = FALSE)
cor.test(MapErrorsGroup2$`total map errors`, AASGroup2, method="spearman", exact = FALSE)
cor.test(MapErrorsGroup2$`total map errors`, DistAbScoreGroup2$TotalScore, method="spearman", exact = FALSE)
cor.test(AASGroup2, DistAbScoreGroup2$TotalScore, method="spearman", exact = FALSE)