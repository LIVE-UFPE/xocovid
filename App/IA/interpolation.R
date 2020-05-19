#setting the worskspace
directory <- getwd()
setwd(directory)

#Loading libraries
library("raster")
library("sp")
library("rgdal")
library("rgeos")
library("sf")
library("gstat")

#This commented section is only for testing the script
#day1 = 'C:/Users/clari/PyCharmProjects/covid-19/casos confirmados/covid19_22-03.csv'
#day2 = 'C:/Users/clari/PyCharmProjects/covid-19/casos confirmados/covid19_23-03.csv'
#day3 = 'C:/Users/clari/PyCharmProjects/covid-19/casos confirmados/covid19_24-03.csv'
#day4 = 'C:/Users/clari/PyCharmProjects/covid-19/casos confirmados/covid19_25-03.csv'
#list_days = list(day1,day2,day3,day4)


# Fetch command line arguments
list_arguments <- commandArgs(trailingOnly = TRUE)
#print(list_arguments)
state <- list_arguments[[5]]

print(state)
print(list_arguments[[6]])
list_days <- c(list_arguments[[1]], list_arguments[[2]], list_arguments[[3]], list_arguments[[4]])
print(list_days)
list_interpolation = c() #store the interpolated data for each day of covid-19 confirmed cases



# define sample grid based on the extent of the state_shp file
#state_shapefile_path <- paste0("shapefiles estados/",state,".shp")
state_shp <- shapefile(list_arguments[[6]])

if(state == 'BR'){
  grid <- spsample(state_shp, type = 'regular', n = 90000)
}

grid <- spsample(state_shp, type = 'regular', n = 10000)


# Distribution map of the confirmed cases of covid-19 for each day (including the predicted)
for (i in 1:4) {
  
  # Loading the .csv data
  covid19 <- read.csv(list_days[[i]])
  str(covid19)
  
  
  #Creating the shapefile for the data interpolation
  shp_covid19 <- st_as_sf(covid19, coords = c("longitude", "latitude"), crs = " +proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0")
  new_shp <- st_write(shp_covid19, "shapefiles/shapefile_interpolacao.shp", append=FALSE)
  
  
  #loading the shapefile of confirmed cases of covid19
  cases.Points <- shapefile("shapefiles/shapefile_interpolacao.shp")
  
  
  # runs the idw for the confirmed cases of covid-19
  idw <- idw(cases.Points$casos ~ 1,cases.Points, newdata= grid)
  idw.output = as.data.frame(idw)
  list_interpolation[[i]] <- idw.output
  
}

#Saving the dataframe prediction
day1_int <- list_interpolation[1]
day2_int <- list_interpolation[2]
day3_int <- list_interpolation[3]
day4_int <- list_interpolation[4]


df <- data.frame("longitude" = day1_int[[1]]$x1,
                 "latitude" = day1_int[[1]]$x2,
                 "day1" = day1_int[[1]]$var1.pred,
                 "day2" = day2_int[[1]]$var1.pred,
                 "day3" = day3_int[[1]]$var1.pred,
                 "day4" = day4_int[[1]]$var1.pred
)

# saving interpolated values into a csv file
split_string <- unlist(strsplit(list_days[4],"_")) 
fileName <- paste0("predicao_covid19",state,"_",split_string[2])
names(df)[1:6] <- c("longitude","latitude","day1","day2","day3","prediction")
write.csv(df, paste0("bases predicao ",state,"/",fileName),row.names = FALSE)







