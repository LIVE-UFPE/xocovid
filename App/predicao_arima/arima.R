#setting the worskspace
directory <- getwd()
setwd(directory)


#Load libraries
library("tseries")
library("forecast")
library("lubridate")

# Fetch command line arguments
print("aaaaaaaaaaaaaaa asdsad asfasf ")
args  <- commandArgs(trailingOnly = TRUE)
cumulativeSum <- args[1]
estado <- args[2]
print(args)

print(args[1])
print(args[2])
print("aaaaaaaaaaaaaaa asdsad asfasf ")

findyear <- function(date){
  #cacth the year in which the time serie begins
  split_string <- unlist(strsplit(as.character(date),"-"))
  year <- split_string[1]
  year <- as.integer(year)
  return(year)
}

dateFormat <- function(dia){
  aux <- unlist(strsplit(as.character(dia),"-"))
  date <- paste0(aux[3],"-",aux[2],"-",aux[1])
  return(date)
}

modelStat <- function(model, real){
  # save a .csv file of the model coefficients
  pearson <- cor(real,model,method = "pearson")
  spearman <- cor(real,model,method = "spearman")
  kendall <- cor(real,model,method = "kendall")
  stats <- c(pearson, spearman, kendall)
  return(stats)
}

# section for testing purposes
#cumulativeSum <- c("base ARIMA/baseARIMA_2020-04-12.csv")
#cumulativeSum <- paste0("/", cumulativeSum)

#Load data

data <- read.csv(cumulativeSum)
class(data)

# Representing the data in a time-series format
start <- findyear(data$dt_notificacao[1])
tsdata <- ts(data$acumulado_confirmados,  frequency = 365, start = decimal_date(as.Date(data$dt_notificacao[1])))
print(tsdata)
write.csv(data,paste0("ts.csv"))
num_pred = 14

#Spliting the data into training and testing dataset
y_train = head(tsdata, n = (length(tsdata) - num_pred))
y_test = tail(tsdata, n = num_pred)
fit <- auto.arima(y_train)

# Adjusting an ARIMA model
fit <- auto.arima(y_train)

##############################################################################
# Send model information
model.stats <- modelStat(y_train,as.numeric(fit$fitted))
df <- data.frame(model.stats[1],model.stats[2],model.stats[3])
names(df) <- c("pearson", "spearman", "kendall")
write.csv(df,paste0("coeficientes modelo/","coefs_m_",dateFormat(data$dt_notificacao[1]),"_",dateFormat(data$dt_notificacao[length(tsdata) - 6]),".csv"))

# Picture model graph
img <- paste0("grafico modelo/","modelo","_",estado,".png")
png(file = img, width=650, height = 500, units = 'px')
write.csv(y_train,paste0("y_train.csv"))
plot(y_train,lwd=2, col='blue',type='l',ylab="Casos confirmados", xlab="Tempo", main=paste0("Casos confirmados da covid-19 em ",estado,dateFormat(data$dt_notificacao[1])," a ",dateFormat(data$dt_notificacao[length(tsdata) - 6])))
grid(lwd = 2, col = 'blue') 
lines(fit$fitted, col='red')
legend("topleft",legend = c("Modelo", "Casos confirmados"), col=c("red","blue"),pch = c("-","-"),text.col = "black",inset = c(0.1, 0.1))
dev.off()

##############################################################################
# Send the prediction information
forecast1 <- forecast(fit, h=num_pred)
pred.stats <- modelStat(y_test,as.numeric(forecast1$mean))
df.pred <- data.frame(pred.stats[1],pred.stats[2],pred.stats[3])
names(df.pred) <- c("pearson", "spearman", "kendall")
write.csv(df.pred,paste0("coeficientes predicao/","coefs_pred_",dateFormat(data$dt_notificacao[length(tsdata) - 5]),"_",dateFormat(data$dt_notificacao[length(tsdata)]),".csv"))

#Prediction graph
img <- paste0("./grafico predicao/","pred","_",estado,".png")
png(file = img, width=650, height = 500, units = 'px')
write.csv(forecast1,paste0("pred_.csv"))
plot(forecast1, lwd =2, type='l',ylab="Casos confirmados", xlab="Tempo", main=paste0("Predição dos casos confirmados da covid-19 em ", estado, dateFormat(data$dt_notificacao[length(tsdata) - 5])," a ",dateFormat(data$dt_notificacao[length(tsdata)])))
grid(lwd = 2, col = 'blue') 
dev.off()

##############################################################################
begin <- dateFormat(as.Date(data$dt_notificacao[length(tsdata)])+1)
end <- dateFormat(as.Date(data$dt_notificacao[length(tsdata)])+6)
fit.p <- auto.arima(tsdata) # build the arima model since the beginning of the dataset
f.proj <- forecast(fit.p, h = num_pred) # forecast for 6 days after the last day of the dataset

# Send proj information
proj.stats <- modelStat(tsdata, fit.p$fitted)
df.proj <- data.frame(proj.stats[1],proj.stats[2],proj.stats[3])
names(df.proj) <- c("pearson", "spearman", "kendall")
write.csv(df.proj,paste0("coeficientes projecao/","coefs_proj_",begin,"_",end,".csv"))

#proj graph

img <- paste0("grafico projecao/","proj",estado,".png")
png(file = img, width=650, height = 500, units = 'px')

write.csv(f.proj,paste0("proj_.csv"))
plot(f.proj,lwd=2, type='l',ylab="Casos confirmados", xlab="Tempo",
main=paste0("Projeção dos casos confirmados da covid-19 em ",estado,begin," a ",end),
)
grid(lwd = 2, col = 'blue') 
dev.off()

