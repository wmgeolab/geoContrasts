
import os
import json
import csv
import urllib.request

#Initialize workspace
ws = {}
try:
    fdsfsfdsfsdf
    ws['working'] = os.environ['GITHUB_WORKSPACE']
    ws['logPath'] = os.path.expanduser("~") + "/tmp/log.txt"
except:
    ws['working'] = os.path.abspath("") # current folder ie releaseData
    ws['logPath'] = "buildMetaData-log.txt" #os.path.expanduser("~") + "/tmp/log.txt"
os.chdir(ws['working'])

#Load in the ISO lookup table
isoDetails = list(csv.DictReader(open("../buildData/iso_3166_1_alpha_3.csv", encoding="utf8")))

#Remove any old CSVs
gbContrastCSV = "geoContrast-meta.csv"
try:
    os.remove(gbContrastCSV)
except:
    pass

#Create output csv file with headers
fieldnames = "boundaryID,boundaryName,boundaryISO,boundaryYearRepresented,boundaryType,boundaryCanonical,boundarySource-1,boundarySource-2,boundaryLicense,licenseDetail,licenseSource,boundarySourceURL,sourceDataUpdateDate,buildUpdateDate,Continent,UNSDG-region,UNSDG-subregion,worldBankIncomeGroup,apiURL,admUnitCount,meanVertices,minVertices,maxVertices,meanPerimeterLengthKM,minPerimeterLengthKM,maxPerimeterLengthKM,meanAreaSqKM,minAreaSqKM,maxAreaSqKM".split(',')
wfob = open(gbContrastCSV, 'w', newline='', encoding='utf8')
writer = csv.DictWriter(wfob, fieldnames=fieldnames)
writer.writeheader()

#Loop all metadata json files in releaseData
for x in []: #(path, dirname, filenames) in os.walk(ws["working"]):

    #Look for file metadata.json
    metaSearch = [x for x in filenames if x.endswith('metaData.json')]
    if(len(metaSearch)==1):
        print(metaSearch)

        #Init row from file metadata.json
        with open(path + "/" + metaSearch[0], "r", encoding='utf8') as j:
            meta = json.load(j)

        #Drop unwanted entries
        meta.pop('downloadURL')

        #Handle some standard missing data...?
        if not meta['boundaryCanonical']:
            meta['boundaryCanonical'] = 'Unknown'

        #Fetch country info
        isoMeta = [row
                   for row in isoDetails
                   if row["Alpha-3code"] == meta['boundaryISO']]
        if len(isoMeta) == 0:
            continue
        else:
            isoMeta = isoMeta[0]

        #Add in country context
        for k in 'Country,Continent,UNSDG-region,UNSDG-subregion,worldBankIncomeGroup'.split(','):
            meta[k] = isoMeta[k]

        #Add in apiURL
        #githubRoot = 'https://raw.githubusercontent.com/wmgeolab/geoContrast/main' # normal github files
        githubRoot = 'https://media.githubusercontent.com/media/wmgeolab/geoContrast/main' # lfs github files
        topoPath = path + "/" + metaSearch[0].replace('-metaData.json', '.topojson')
        topoPath = topoPath.replace('\\','/')
        relTopoPath = topoPath[topoPath.find('releaseData'):]
        meta['apiURL'] =  githubRoot + '/' + relTopoPath

        #Calculate geometry statistics
        #(Commented geometry/stats code below is old, needs to be updated)
##        #We'll use the geoJSON here, as the statistics (i.e., vertices) will be most comparable
##        #to other cases.
####        geojsonSearch = [x for x in filenames if re.search('.geojson', x)]
####        with open(path + "/" + geojsonSearch[0], "r") as g:
####            geom = geopandas.read_file(g)
####        
####        admCount = len(geom)
####        
####        vertices=[]
####        for i, row in geom.iterrows():
####            n = 0
####            
####            if(row.geometry.type.startswith("Multi")):
####                for seg in row.geometry:
####                    n += len(seg.exterior.coords)
####            else:
####                n = len(row.geometry.exterior.coords)
####            
####            vertices.append(n) ###
##
##        admCount = ''
##        stat1 = '' #round(sum(vertices)/len(vertices),0)
##        stat2 = '' #min(vertices)
##        stat3 = '' #max(vertices)
##        
##        metaLine = metaLine + str(admCount) + '","' + str(stat1) + '","' + str(stat2) + '","' + str(stat3) + '","'
##
##        #Perimeter Using WGS 84 / World Equidistant Cylindrical (EPSG 4087)
####        lengthGeom = geom.copy()
####        lengthGeom = lengthGeom.to_crs(epsg=4087)
####        lengthGeom["length"] = lengthGeom["geometry"].length / 1000 #km
##
##        stat1 = '' #lengthGeom["length"].mean()
##        stat2 = '' #lengthGeom["length"].min()
##        stat3 = '' #lengthGeom["length"].max()
##        metaLine = metaLine + str(stat1) + '","' + str(stat2) + '","' + str(stat3) + '","'
##
##        #Area #mean min max Using WGS 84 / EASE-GRID 2 (EPSG 6933)
####        areaGeom = geom.copy()
####        areaGeom = areaGeom.to_crs(epsg=6933)
####        areaGeom["area"] = areaGeom['geometry'].area / 10**6 #sqkm
##
##        stat1 = '' #areaGeom['area'].mean()
##        stat2 = '' #areaGeom['area'].min()
##        stat3 = '' #areaGeom['area'].max()
##        
##        metaLine = metaLine + str(stat1) + '","' + str(stat2) + '","' + str(stat3) + '","'

        # write row
        #print(meta)
        writer.writerow(meta)

#Add in csv entries based on the github geoBoundaries (Open) metadata file
rfob = urllib.request.urlopen('https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/geoBoundariesOpen-meta.csv')
reader = csv.DictReader(rfob.read().decode('utf-8').split('\n'))
for row in reader:
    # drop any additional 'blank' field values beyond fieldnames
    if '' in row.keys(): row.pop('')
    if None in row.keys(): row.pop(None)
    # clear and set the source fields to 'geoBoundaries'
    # TODO: maybe the better way is to include an extra field that says the geoContrast source dataset
    row['boundarySource-1'] = 'geoBoundaries (Open)'
    row['boundarySource-2'] = ''
    # overwrite the gb apiURL with direct link to github
    iso = row['boundaryISO']
    lvl = row['boundaryType']
    apiURL = 'https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/gbOpen/{iso}/{lvl}/geoBoundaries-{iso}-{lvl}.topojson'.format(iso=iso, lvl=lvl)
    row['apiURL'] = apiURL
    print(apiURL)
    # fix gb url bugs
    row['licenseSource'] = row['licenseSource'].replace('https//','https://').replace('http//','http://')
    row['boundarySourceURL'] = row['boundarySourceURL'].replace('https//','https://').replace('http//','http://')
    # write ro row
    writer.writerow(row)

#Add in csv entries based on the github geoBoundaries (Humanitarian) metadata file
rfob = urllib.request.urlopen('https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/geoBoundariesHumanitarian-meta.csv')
reader = csv.DictReader(rfob.read().decode('utf-8').split('\n'))
for row in reader:
    # drop any additional 'blank' field values beyond fieldnames
    if '' in row.keys(): row.pop('')
    if None in row.keys(): row.pop(None)
    # clear and set the source fields to 'geoBoundaries'
    # TODO: maybe the better way is to include an extra field that says the geoContrast source dataset
    row['boundarySource-1'] = 'geoBoundaries (Humanitarian)'
    row['boundarySource-2'] = ''
    # overwrite the gb apiURL with direct link to github
    iso = row['boundaryISO']
    lvl = row['boundaryType']
    apiURL = 'https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/gbHumanitarian/{iso}/{lvl}/geoBoundaries-{iso}-{lvl}.topojson'.format(iso=iso, lvl=lvl)
    row['apiURL'] = apiURL
    print(apiURL)
    # fix gb url bugs
    row['licenseSource'] = row['licenseSource'].replace('https//','https://').replace('http//','http://')
    row['boundarySourceURL'] = row['boundarySourceURL'].replace('https//','https://').replace('http//','http://')
    # write ro row
    writer.writerow(row)

#Add in csv entries based on the github geoBoundaries (Authoritative) metadata file
rfob = urllib.request.urlopen('https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/geoBoundariesAuthoritative-meta.csv')
reader = csv.DictReader(rfob.read().decode('utf-8').split('\n'))
for row in reader:
    # drop any additional 'blank' field values beyond fieldnames
    if '' in row.keys(): row.pop('')
    if None in row.keys(): row.pop(None)
    # clear and set the source fields to 'geoBoundaries'
    # TODO: maybe the better way is to include an extra field that says the geoContrast source dataset
    row['boundarySource-1'] = 'geoBoundaries (Authoritative)'
    row['boundarySource-2'] = ''
    # overwrite the gb apiURL with direct link to github
    iso = row['boundaryISO']
    lvl = row['boundaryType']
    apiURL = 'https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/gbAuthoritative/{iso}/{lvl}/geoBoundaries-{iso}-{lvl}.topojson'.format(iso=iso, lvl=lvl)
    row['apiURL'] = apiURL
    print(apiURL)
    # fix gb url bugs
    row['licenseSource'] = row['licenseSource'].replace('https//','https://').replace('http//','http://')
    row['boundarySourceURL'] = row['boundarySourceURL'].replace('https//','https://').replace('http//','http://')
    # write ro row
    writer.writerow(row)

#Close up shop
wfob.close()


