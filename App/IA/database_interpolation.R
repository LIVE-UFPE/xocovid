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

# Fetch command line arguments
list_days <- commandArgs(trailingOnly = TRUE)
list_interpolation = list() #store the interpolated data for each day of covid-19 confirmed cases


# define sample grid based on the extent of the recife_shp file
recife_shp <- shapefile("shapefile/RECIFE_WGS84.shp") # Recife's shapefile must be stored
grid <- spsample(recife_shp, type = 'regular', n = 10000)

for (i in 1:4) {
  
  # Loading the .csv data
  covid19 <- read.csv(list_days[i])
  str(covid19)
  
  
  #Creating the shapefile for the data interpolation
  #shp <- st_read("shapefile/NOVO RECIFE.shp")
  shp_covid19 <- st_as_sf(covid19, coords = c("longitude", "latitude"), crs = " +proj=utm +zone=25 +south +ellps=GRS80 +units=m +no_defs 
")
  shp_wgs84 <- st_transform(shp_covid19, crs(recife_shp))
  new_shp <- st_write(shp_wgs84, "shapefile/shapefile_interpolacao.shp", append=FALSE)
  

  #loading the shapefile of confirmed cases of covid19
  cases.Points <- shapefile("shapefile/shapefile_interpolacao.shp")
  
 
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

# saving interpolated values into a .csv file
split_string <- unlist(strsplit(list_days[4],"_")) 
fileName <- paste0("predicao_covid19_",split_string[2])
names(df)[1:6] <- c("longitude","latitude","day1","day2","day3","prediction")
write.csv(df, paste0("bases predicao/",fileName),row.names = FALSE)







