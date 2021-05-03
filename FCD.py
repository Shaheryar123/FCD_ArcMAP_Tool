import arcpy
import os
arcpy.env.workspace = arcpy.GetParameterAsText(0)
band1 = arcpy.GetParameterAsText(1)
band2 = arcpy.GetParameterAsText(2)
band3 = arcpy.GetParameterAsText(3)
band4 = arcpy.GetParameterAsText(4)
band5 = arcpy.GetParameterAsText(5)


outStatFile = "\stats.txt"
arcpy.sa.BandCollectionStats([band1, band2,band3,band4,band5], outStatFile, "BRIEF")
import pandas as pd
data = pd.read_csv(arcpy.env.workspace + '\stats.txt', header = None,skiprows=0)
frame = pd.DataFrame(data)
frame.to_csv(arcpy.env.workspace +'\stats.csv')
data1 = pd.read_csv(arcpy.env.workspace +'\stats.csv', header = None,skiprows=3)

for i in range(1,6):
    location = data1.loc[i,1]
    slice = location.split()
    min,max,mean,std = float(slice[1]),float(slice[2]),float(slice[3]),float(slice[4]) 
    X1 = mean - (2*std)
    X2 = mean + (2*std)
    A = (min-max)/(X1-X2)
    B = -(A*X1)+X2
   
    def Normalization(x,y,z):
        #z = z + 1
        if z == 1:
        
            nm1 = x * arcpy.Raster(band1) + y
            nm1.save("newnm1.tif")
           
        if z == 2:
            
            nm2 = x * arcpy.Raster(band2) + y
            nm2.save("newnm2.tif")
            
        if z == 3:
            
            nm3 = x * arcpy.Raster(band3) + y
            nm3.save("newnm3.tif")
            
        if z == 4:
            
            nm4 = x * arcpy.Raster(band4) + y
            nm4.save("newnm4.tif")
            
        if z == 5:
            nm5 = x * arcpy.Raster(band5) + y
            nm5.save("newnm5.tif")  
            
    Normalization(A,B,i)

os.remove(arcpy.env.workspace +"\stats.txt")
os.remove(arcpy.env.workspace +"\stats.csv")    

b43 = arcpy.Raster("newnm4.tif") - arcpy.Raster("newnm3.tif")
b43.save("b43.tif")
b43gt = arcpy.Raster("b43.tif") > 0
b43gt.save("b43gt.tif")
AV = (arcpy.Raster("newnm4.tif") + 1) * (65536 - arcpy.Raster("newnm3.tif")) * (arcpy.Raster("b43gt.tif"))
AV.save("AV.tif")
AVI =  arcpy.Raster("AV.tif") ** 0.333333
AVI.save("AVI.tif")
arcpy.gp.RescaleByFunction_sa("AVI.tif", "AVI_rescale.tif", "LINEAR  #  #  #  #  #  #", "1", "100")


barenu = (arcpy.Raster("newnm5.tif") + arcpy.Raster("newnm3.tif")) - (arcpy.Raster("newnm4.tif") + arcpy.Raster("newnm1.tif"))
barenu.save("barenu.tif")
baredeno = (arcpy.Raster("newnm5.tif") + arcpy.Raster("newnm3.tif")) + (arcpy.Raster("newnm4.tif") + arcpy.Raster("newnm1.tif"))
baredeno.save("baredeno.tif")
BI = (arcpy.Raster("barenu.tif") / arcpy.Raster("baredeno.tif")) * 100 +100
BI.save("BI.tif")
arcpy.gp.RescaleByFunction_sa("BI.tif", "BI_rescale.tif", "LINEAR  #  #  #  #  #  #", "1", "100")

arcpy.gp.PrincipalComponents_sa("BI.tif;AVI_rescale.tif", "VD.tif", "1", "")
shadowindex = (65536 - arcpy.Raster("newnm1.tif"))*(65536 - arcpy.Raster("newnm2.tif"))*(65536 - arcpy.Raster("newnm3.tif"))
shadowindex.save("shadowindex.tif")
SI = arcpy.Raster("shadowindex.tif") ** 0.333333
SI.save("SI.tif")
arcpy.gp.RescaleByFunction_sa("SI.tif", "SSI.tif", "LINEAR  #  #  #  #  #  #", "1", "100")

canopy = (arcpy.Raster("VD.tif") * arcpy.Raster("SSI.tif")) + 1
canopy.save("canopy.tif")
forest = arcpy.Raster("canopy.tif") ** 0.5
forest.save("forest.tif")
FCD = arcpy.Raster("forest.tif") - 1
FCD.save("FCD.tif")

outReclass3 = arcpy.sa.Reclassify("FCD.tif", "Value", arcpy.sa.RemapRange([[1,25,1],[25,50,2],[50,75,3],[75,100,4]]), "NODATA")
outReclass3.save("FCDreclass.tif")
arcpy.Delete_management("newnm1.tif")
arcpy.Delete_management("newnm2.tif")
arcpy.Delete_management("newnm3.tif")
arcpy.Delete_management("newnm4.tif")
arcpy.Delete_management("newnm5.tif")
arcpy.Delete_management("forest.tif")
arcpy.Delete_management("canopy.tif")
arcpy.Delete_management("AV.tif")
arcpy.Delete_management("b43.tif")
arcpy.Delete_management("b43gt.tif")
arcpy.Delete_management("barenu.tif")
arcpy.Delete_management("baredeno.tif")
arcpy.Delete_management("canopy.tif")
arcpy.Delete_management("shadowindex.tif")


