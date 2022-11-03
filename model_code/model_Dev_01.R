---
title: "model_Dev_1"
output: html_document
date: '2022-10-29'
---
  
rm(list=ls())

library(tidyverse)
library(caret)
library(ggplot2)
library(pROC)
library(corrplot)
library(ggcorrplot)
library(dplyr)
library(lubridate)

setwd("~/MS_Analytics/CSE_6242_Data_and_Visual_Analytics/Project")

#Load Data
LA_data <- read.csv("la_data_full.csv")


#Make date columns
LA_data[['Start_Time']] <- as.POSIXct(LA_data[['Start_Time']],
                                      format = "%Y-%m-%d %H:%M:%S")

LA_data[['Start_Hour']] <- as.integer(format(LA_data$Start_Time, format="%H"))
LA_data[['Start_Minute']] <- as.integer(format(LA_data$Start_Time, format="%M"))
LA_data[['Start_Second']] <- as.integer(format(LA_data$Start_Time, format="%S"))
LA_data[['Start_Year']] <- as.integer(format(LA_data$Start_Time, format="%Y"))
LA_data[['Start_Month']] <- as.integer(format(LA_data$Start_Time, format="%m"))
LA_data[['Start_Day']] <- as.integer(format(LA_data$Start_Time, format="%d"))

LA_data[['Weekday']] <- wday(LA_data$Start_Time, label=TRUE)

#Remove Start_Time
LA_fit_data <- LA_data %>% select(-one_of("Start_Time"))

#Remove NA values
remove_NA <- na.omit(LA_fit_data)

# #Check all binary variables
# "True" %in% LA_fit_data$Amenity
# "True" %in% LA_fit_data$Bump
# "True" %in% LA_fit_data$Crossing
# "True" %in% LA_fit_data$Give_Way
# "True" %in% LA_fit_data$Junction
# "True" %in% LA_fit_data$No_Exit
# "True" %in% LA_fit_data$Railway
# "True" %in% LA_fit_data$Roundabout
# "True" %in% LA_fit_data$Station
# "True" %in% LA_fit_data$Stop
# "True" %in% LA_fit_data$Traffic_Calming
# "True" %in% LA_fit_data$Traffic_Signal
# "True" %in% LA_fit_data$Turning_Loop

# #Check all binary variables
# "True" %in% remove_NA$Amenity
# "True" %in% remove_NA$Bump
# "True" %in% remove_NA$Crossing
# "True" %in% remove_NA$Give_Way
# "True" %in% remove_NA$Junction
# "True" %in% remove_NA$No_Exit
# "True" %in% remove_NA$Railway
# "True" %in% remove_NA$Roundabout
# "True" %in% remove_NA$Station
# "True" %in% remove_NA$Stop
# "True" %in% remove_NA$Traffic_Calming
# "True" %in% remove_NA$Traffic_Signal

#Remove Turning_Loop
LA_fit_data <- LA_fit_data %>% select(-"Turning_Loop")

# #Plot barplots for binary data
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Amenity)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Bump)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Crossing)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Give_Way)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Junction)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = No_Exit)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Railway)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Roundabout)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Station)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Stop)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Traffic_Calming)) + 
#   geom_bar(position = "stack")
# 
# ggplot(na.omit(LA_fit_data), aes(x = Target, fill = Traffic_Signal)) + 
#   geom_bar(position = "stack")


#Create correlation matrix
#model.matrix(~0+., data=remove_NA) %>% cor(use="pairwise.complete.obs") %>%
#  ggcorrplot(show.diag = F, type="lower", lab=TRUE, lab_size=2)

pressure_model <- lm(Target ~ Pressure.in., data=LA_fit_data, na.action=na.omit)
summary(pressure_model)

#Pressure vs. Target scatterplot
plot(remove_NA$Pressure.in., remove_NA$Target, xlab="Pressure", ylab="Target")
hist(remove_NA$Pressure.in.)


#Convert pressure from hPa to inches of mercury
LA_fit_data <- LA_fit_data %>% mutate(Pressure.in. = 
                                        case_when(Target == 0 ~ Pressure.in./33.86388666667,
                                                  Target == 1 ~ Pressure.in.))

pressure_model_2 <- lm(Target ~ Pressure.in., data=LA_fit_data, na.action=na.omit)
summary(pressure_model_2)
remove_NA_2 <- na.omit(LA_fit_data)

plot(remove_NA_2$Pressure.in., remove_NA_2$Target, xlab="Pressure", ylab="Target")
hist(remove_NA_2$Pressure.in.)

#Fixed pressure
model.matrix(~0+., data=remove_NA_2) %>% cor(use="pairwise.complete.obs") %>%
  ggcorrplot(show.diag = F, type="lower", lab=TRUE, lab_size=2)


#Start trying models
#Don't use - multiple linear regression
initial_model <- lm(Target ~ ., data=LA_fit_data, na.action=na.omit)

summary(initial_model)
#plot(initial_model)

# amenity_logit_model <- glm(Target ~ Amenity, family=binomial(), data=LA_fit_data, na.action=na.omit)
# bump_logit_model <- glm(Target ~ Bump, family=binomial(), data=LA_fit_data, na.action=na.omit)
# crossing_logit_model <- glm(Target ~ Crossing, family=binomial(), data=LA_fit_data, na.action=na.omit)
# give_way_logit_model <- glm(Target ~ Give_Way, family=binomial(), data=LA_fit_data, na.action=na.omit)
# junction_logit_model <- glm(Target ~ Junction, family=binomial(), data=LA_fit_data, na.action=na.omit)
# no_exit_logit_model <- glm(Target ~ No_Exit, family=binomial(), data=LA_fit_data, na.action=na.omit)
# railway_logit_model <- glm(Target ~ Railway, family=binomial(), data=LA_fit_data, na.action=na.omit)
# roundabout_logit_model <- glm(Target ~ Roundabout, family=binomial(), data=LA_fit_data, na.action=na.omit)
# station_logit_model <- glm(Target ~ Station, family=binomial(), data=LA_fit_data, na.action=na.omit)
# stop_logit_model <- glm(Target ~ Stop, family=binomial(), data=LA_fit_data, na.action=na.omit)
# traffic_calming_logit_model <- glm(Target ~ Traffic_Calming, family=binomial(), data=LA_fit_data, na.action=na.omit)
# traffic_signal_logit_model <- glm(Target ~ Traffic_Signal, family=binomial(), data=LA_fit_data, na.action=na.omit)


#Logistic Regression
ini_logit_model <- glm(Target ~ ., family=binomial(), data=LA_fit_data, na.action=na.omit)

ini_logit_model <- glm(Target ~ Start_Lat+Start_Lng+Temperature.F.+
                     Humidity...+Pressure.in.+Wind_Speed.mph.+Precipitation.in.+
                     Amenity+Bump+Crossing+Give_Way+Junction+
                     No_Exit+Railway+Roundabout+Station+Stop+Traffic_Calming+
                     Traffic_Signal+Weekday+Start_Hour+Start_Month,
                   family=binomial(), data=LA_fit_data,
                   na.action=na.omit)
#Removed starting minute, second, year, and day
# summary(check_logit)

# ini_logit_model <- glm(Target ~ Start_Lat+Start_Lng+Temperature.F.+
#                          Humidity...+Pressure.in.+Wind_Speed.mph.+Precipitation.in.
#                        +Amenity+Bump+Crossing+Give_Way+Junction+
#                          No_Exit+Railway+Roundabout+Station+Stop+Traffic_Calming+
#                          Traffic_Signal+Start_Hour+Start_Minute+Start_Second+
#                          Weekday+Start_Year+Start_Month+Start_Day
#                        , family=binomial(), data=LA_fit_data, na.action=na.omit)

summary(ini_logit_model)

predicted <- predict(ini_logit_model, remove_NA_2, type="response")

auc(remove_NA_2$Target, predicted)

#Confusion Matrix
confusionMatrix(as.factor(remove_NA_2$Target), as.factor(round(predicted, digits=0)))


#Separate into 10 k folds for cross validation

#Set a reproducible random sampling
set.seed(12)

train_control <- trainControl(method = "cv", number = 10)

CV_model <- train(Target ~ Start_Lat+Start_Lng+Temperature.F.+
                    Humidity...+Pressure.in.+Wind_Speed.mph.+Precipitation.in.+
                    Amenity+Bump+Crossing+Give_Way+Junction+
                    No_Exit+Railway+Roundabout+Station+Stop+Traffic_Calming+
                    Traffic_Signal+Weekday+Start_Hour+Start_Month,
                  data = LA_fit_data, method = "glm", family= "binomial",
                  na.action=na.omit, trControl = train_control)

summary(CV_model)
print(CV_model)

predicted_cross <- predict(CV_model, remove_NA_2)

auc(remove_NA_2$Target, predicted_cross)

confusionMatrix(as.factor(remove_NA_2$Target), as.factor(round(predicted_cross, digits=0)))
