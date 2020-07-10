import pandas as pd
import numpy as np

import shutil

import multiprocessing.pool

import matplotlib.dates
import matplotlib.pyplot as plt
import matplotlib.cbook
import matplotlib.cm

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

from matplotlib import colors as mcolors
from postgreSQLSuite import *

log = logging.getLogger(__name__)
log.setLevel(DEBUG)

try:
    from osgeo import ogr, osr, gdal
except Exception as e:
    log.error(f"Error {e} occured while importing osgeo")


pd.options.display.width = 1000
pd.options.display.max_columns=999
pd.options.display.max_rows=100


def _rasterizeTimesliceWorker(df, rasterPath, imagePath, vmin, vmax, dt, xres, yres, perform_rasterization=True):
    """
      Timeslices rasterize worker
      Rasters a timeslice based on a pd.DataFrame using GDAL by first converting the timeslice to a
      OGR vector layer and then rasterizing the content to a raster layer using GDAL

      :param df: dictionary containing timeslices in format hour:minute:timeslice
      :param rasterPath: path to folder where rasters should be stored
      :param imagePath: path to folder where images should be stored
      :param vmin: minimum data value (number of available vehicles) on all to-be-rastered dataframes
      :param vmax: maximum data value (number of available vehicles) on all to-be-rastered dataframes
      :param xres: width of rastered image
      :param yres: height of rastered image
      :param perform_rasterization: whether or not to raster GDAL layers or just create and store them
      """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    lats = list(df.lat.values)
    lons = list(df.lon.values)
    values = list(df.countReachable.values)

    raster_fn = os.path.join(imagePath, f"{dt.strftime('%d.%m.%y')}-{dt.strftime('%H-%M')}-{xres}-{yres}.tiff")
    vector_fn = os.path.join(rasterPath, f"{dt.strftime('%d.%m.%y')}-{dt.strftime('%H-%M')}.shp")

    # check if vector layer already exists, otherwise create new one and convert values from df to layer
    if not os.path.isfile(vector_fn):
        outsrc = driver.CreateDataSource(vector_fn)
        outlayer = outsrc.CreateLayer(vector_fn, srs, ogr.wkbPoint)
        outlayer.CreateField(ogr.FieldDefn("color_r"), ogr.OFTInteger)
        outlayer.CreateField(ogr.FieldDefn("color_g"), ogr.OFTInteger)
        outlayer.CreateField(ogr.FieldDefn("color_b"), ogr.OFTInteger)

        normalizer = mcolors.Normalize(vmin=vmin, vmax=vmax)
        cmap = matplotlib.cm.get_cmap("hot")

        for idx in range(len(lats)):
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(float(lats[idx]), float(lons[idx]))

            color = cmap(normalizer(values[idx]))
            c_r = int(color[0] * 255)
            c_g = int(color[1] * 255)
            c_b = int(color[2] * 255)

            feature = ogr.Feature(outlayer.GetLayerDefn())
            feature.SetGeometry(point)
            feature.SetField("color_r", c_r)
            feature.SetField("color_g", c_g)
            feature.SetField("color_b", c_b)

            outlayer.CreateFeature(feature)
            feature = None # explicitly set feature to None, indicating to OGR that the content should now be stored
        outsrc = None # explicitly set vector layer to None, indicating to OGR that the content should now be stored

    if perform_rasterization:
        NoData_value = 0

        # Open the data source and read in the extent
        source_ds = ogr.Open(vector_fn)
        source_layer = source_ds.GetLayer()
        xmin, xmax, ymin, ymax = source_layer.GetExtent()


        # Create the destination data source
        x_pixel_size = ((xmax - xmin) / xres)
        y_pixel_size = ((ymax - ymin) / yres)


        target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, xres, yres, 3, gdal.GDT_Byte)
        target_ds.SetGeoTransform((xmin, x_pixel_size, 0, ymax, 0, -y_pixel_size))

        # use three bands to encode colors
        band1 = target_ds.GetRasterBand(1)
        band1.SetNoDataValue(NoData_value)

        band2 = target_ds.GetRasterBand(2)
        band2.SetNoDataValue(NoData_value)

        band3 = target_ds.GetRasterBand(3)
        band3.SetNoDataValue(NoData_value)

        gdal.RasterizeLayer(target_ds, [1], source_layer, options = ["ATTRIBUTE=color_r", "MERGE_ALG=ADD", "ALL_TOUCHED=TRUE"])
        gdal.RasterizeLayer(target_ds, [2], source_layer, options = ["ATTRIBUTE=color_g", "MERGE_ALG=ADD", "ALL_TOUCHED=TRUE"])
        gdal.RasterizeLayer(target_ds, [3], source_layer, options = ["ATTRIBUTE=color_b", "MERGE_ALG=ADD", "ALL_TOUCHED=TRUE"])

    return dt


def rasterizeTimeslices(timeslices: dict, slice_datetime: datetime.datetime, rasterPath: str, imagePath: str, perform_rasterization=True, xres=1000, yres=1000):
    """
    Rasterize timeslices of one day using GDAL

    :param timeslices: dictionary containing timeslices in format hour:minute:timeslice
    :param slice_datetime: datetime indicating begin of timeslices
    :param rasterPath: path to folder where rasters should be stored
    :param imagePath: path to folder where images should be stored
    :param perform_rasterization: whether or not to raster GDAL layers or just create and store them
    :param xres: width of rastered image
    :param yres: height of rastered image
    """

    log.info(f"Rasterizing timeslices")
    if not os.path.isdir(rasterPath):
        log.warning(f"{rasterPath} does not exist, attempting to create folder..")
        os.mkdir(rasterPath)

    if not os.path.isdir(imagePath):
        log.warning(f"{imagePath} does not exist, attempting to create folder..")
        os.mkdir(imagePath)

    maxAgents = 0
    minAgents = 4000
    for hour in sorted(list(timeslices.keys())):
        for minute in timeslices[hour]:
            minAgents = min(minAgents, timeslices[hour][minute][timeslices[hour][minute].countReachable > 3].countReachable.min())
            maxAgents = max(maxAgents, timeslices[hour][minute].countReachable.max())

    multproc = True
    hours = sorted(timeslices.keys())
    minutes = range(0, 60, 10)

    global parsed
    parsed = 0

    maxParsed = len(hours)*len(minutes)
    steps = 10
    iter = int(maxParsed / steps)

    def callback(result):
        dt = result
        c_hour = dt.hour
        c_minute = dt.minute
        global parsed
        parsed += 1
        numBlocks = int(parsed / (iter + 1)) if parsed != maxParsed else steps
        print(f"\rRendering timeslices [" + ''.join(['#' for _ in range(numBlocks)]).ljust(steps) + f"] ({str(c_hour).rjust(2)} {str(c_minute).rjust(2)})", end="", flush=True)



    if multproc:
        pool = multiprocessing.Pool()
        for hour in hours:
            for minute in sorted(list(timeslices[hour].keys())):
                dt = datetime.datetime(year=slice_datetime.year, month=slice_datetime.month, day=slice_datetime.day, hour=hour, minute=minute)
                pool.apply_async(_rasterizeTimesliceWorker,
                                 (timeslices[hour][minute], rasterPath, imagePath, minAgents, maxAgents, dt, xres, yres, perform_rasterization),
                                 callback=callback)
        pool.close()
        pool.join()
    else:
        for hour in hours:
            for minute in minutes:
                dt = datetime.datetime(year=slice_datetime.year, month=slice_datetime.month, day=slice_datetime.day, hour=hour, minute=minute)
                callback(_rasterizeTimesliceWorker(timeslices[hour][minute], rasterPath, imagePath, minAgents, maxAgents, dt, xres, yres, perform_rasterization))
    print()


def rasterizeTimesliceMultipleDays(timeslices_range: dict, perform_rasterization):
    """
    Rasterize timeslices over multiple days while keeping consistent color scheme across rasters

    timeslices_range shall for each day contain a dictioanry with keys:
    - timeslices
    - startTime
    - endTime
    - imagePath
    - rasterPath

    :param timeslices_range: dictionary containing timeslices and metadata for each day
    :param perform_rasterization: whether or not to raster GDAL layers or just create and store them
    """

    xres = 1000
    yres = 1000
    multproc = True

    min_agents_range = 4000
    max_agents_range = 0

    log.info(f"Calculating min and max agents over all timeslices")
    for day in timeslices_range:
        timeslices = timeslices_range[day]["timeslices"]
        for hour in sorted(list(timeslices.keys())):
            for minute in timeslices[hour]:
                min_agents_range = min(min_agents_range, timeslices[hour][minute][timeslices[hour][minute].countReachable > 3].countReachable.min())
                max_agents_range = max(max_agents_range, timeslices[hour][minute].countReachable.max())

    log.info(f"min agents: {min_agents_range}, max agents: {max_agents_range}")


    hours = range(0,24)
    minutes = range(0, 60, 10)
    log.info(f"Rasterizing timeslices from {timeslices_range[list(timeslices_range.keys())[0]]['startTime']} to {timeslices_range[list(timeslices_range.keys())[-1]]['startTime']}")
    for day in timeslices_range:
        timeslices = timeslices_range[day]["timeslices"]
        rasterPath = timeslices_range[day]["rasterPath"]
        imagePath = timeslices_range[day]["imagePath"]
        slice_datetime = timeslices_range[day]["startTime"]

        log.info(f"Rasterizing timeslices on day {day}")
        if not os.path.isdir(rasterPath):
            log.warning(f"{rasterPath} does not exist, attempting to create folder..")
            os.mkdir(rasterPath)

        if not os.path.isdir(imagePath):
            log.warning(f"{imagePath} does not exist, attempting to create folder..")
            os.mkdir(imagePath)

        global parsed
        parsed = 0

        maxParsed = len(hours)*len(minutes)
        steps = 10
        iter = int(maxParsed / steps)

        def callback(result):
            dt = result
            c_hour = dt.hour
            c_minute = dt.minute
            global parsed
            parsed += 1
            numBlocks = int(parsed / (iter + 1)) if parsed != maxParsed else steps
            print(f"\rRendering timeslices [" + ''.join(['#' for _ in range(numBlocks)]).ljust(steps) + f"] ({str(c_hour).rjust(2)} {str(c_minute).rjust(2)})", end="", flush=True)



        if multproc:
            pool = multiprocessing.Pool()
            for hour in hours:
                for minute in minutes:
                    dt = datetime.datetime(year=slice_datetime.year, month=slice_datetime.month, day=slice_datetime.day, hour=hour, minute=minute)
                    pool.apply_async(_rasterizeTimesliceWorker,
                                     (timeslices[hour][minute], rasterPath, imagePath, min_agents_range, max_agents_range, dt, xres, yres, perform_rasterization),
                                     callback=callback)
            pool.close()
            pool.join()
        else:
            for hour in hours:
                for minute in minutes:
                    dt = datetime.datetime(year=slice_datetime.year, month=slice_datetime.month, day=slice_datetime.day, hour=hour, minute=minute)
                    callback(_rasterizeTimesliceWorker(timeslices[hour][minute], rasterPath, imagePath, min_agents_range, max_agents_range, dt, xres, yres, perform_rasterization))
        print()
        shutil.rmtree(rasterPath)


def visualizeOverview(timeslices: dict, imagePath: str, startTime: datetime.datetime, endTime: datetime.datetime, write_out: bool = False):
    """
    Visualize multiple timeslices by a line graph representing the minimum, mean and maximum number of usable vehicles per timeslice

    :param timeslices: dictionary containing timeslices in format hour:minute:timeslice
    :param imagePath: path to dictionary where output image should be stored
    :param startTime: datetime representing begin of timeslices
    :param endTime: datetime representing end of timeslices
    :param write_out: whether or not to write image and overviewDf to disk
    """

    maxAgents = 0
    minAgents = 4000
    meanAgents = []
    maxs = []
    mins = []
    means = []
    idxs = []

    df_data = []
    for hour in sorted(list(timeslices.keys())):
        for minute in sorted(list(timeslices[hour].keys())):
            minVal =  timeslices[hour][minute][timeslices[hour][minute].countReachable > 5].countReachable.min()
            maxVal =  timeslices[hour][minute][timeslices[hour][minute].countReachable > 5].countReachable.max()
            meanVal = timeslices[hour][minute][timeslices[hour][minute].countReachable > 5].countReachable.mean()

            idx = datetime.datetime(year=startTime.year, month=startTime.month, day=startTime.day, hour=hour, minute=minute)
            idxs.append(idx)

            mins.append(minVal)
            maxs.append(maxVal)
            means.append(meanVal)

            minAgents = min(minAgents, minVal)
            maxAgents = max(maxAgents, maxVal)
            meanAgents.append(meanVal)
            df_data.append([idx, minVal, meanVal, maxVal])


    meanAgents = int(np.mean(meanAgents))
    log.debug(f"Minimum agents at one spot: {minAgents}, mean agents: {meanAgents}, maximum agents: {maxAgents}")

    fig: plt.Figure = plt.figure(figsize=(15, 8), dpi=300)
    ax: plt.Axes = plt.gca()

    ax.plot_date(idxs, mins, '-g', label="minimum")
    ax.plot_date(idxs, means, '-y', label="avgerage")
    ax.plot_date(idxs, maxs, '-r', label="maximum")

    ax.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(byminute=0))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))

    ax.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator(byminute=10))

    ax.set_xlim(datetime.datetime(year=startTime.year, month=startTime.month, day=startTime.day, hour=0, minute=0),
                datetime.datetime(year=startTime.year, month=startTime.month, day=startTime.day, hour=23, minute=59), emit=False)

    ax.set_ylim(250,900)

    fig.autofmt_xdate()
    ax.legend()
    plt.title(f"Minimum, average and maximum number of vehicles seamlessly reaching one vertex, per 10 minute timeslice")
    plt.xlabel(f"time\nat {startTime.strftime('%d.%m.%y')}")
    plt.ylabel("number of seamlessly reaching vehicles")

    overview_df = pd.DataFrame(df_data, columns=["idx", "min", "mean", "max"])
    if write_out:
        overview_df.to_csv(os.path.join(imagePath, f"analysis-{startTime.strftime('%d.%m.%y')}-{endTime.strftime('%d.%m.%y')}.csv"))
        plt.savefig(os.path.join(imagePath, f"analysis-{startTime.strftime('%d.%m.%y')}-{endTime.strftime('%d.%m.%y')}.png"))

