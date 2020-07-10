from analyzer import *
from exporter import *

import pytz
import shutil
import argparse

logging.getLogger("cacher").setLevel(INFO)
logging.getLogger("analyzer").setLevel(DEBUG)
logging.getLogger("pickupDropoff").setLevel(ERROR)
logging.getLogger("postgreSQLSuite").setLevel(WARNING)

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

pd.options.display.width = 1000
pd.options.display.max_columns=999
pd.options.display.max_rows=20

def localize_dates_offset(year, month, day, offset) -> (datetime.datetime, datetime.datetime):
    startDate = pytz.timezone("Europe/Berlin").localize(datetime.datetime(year=year, month=month, day=day + offset))
    endDate = pytz.timezone("Europe/Berlin").localize(datetime.datetime(year=year, month=month, day=day + offset + 1))
    return startDate, endDate

def date_wrapper(s):
    try:
        print(s)
        return pytz.timezone("Europe/Berlin").localize(datetime.datetime.strptime(s, "%d.%m.%y"))
    except ValueError as e:
        log.error(f"Value Error {e} on input {s}")
        raise e
def time_wrapper(s):
    try:
        return pytz.timezone("Europe/Berlin").localize(datetime.datetime.strptime(s, "%H:%M"))
    except ValueError as e:
        log.error(f"Value Error {e} on input {s}")
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-cp",  "--csvPath",                help="full path to csv file", default="./df_parking.csv")

    parser.add_argument("-cpa", "--cachePath",              help="path to directory where caches should be stored",             default="./caches")
    parser.add_argument("-tsp", "--timeslicesPath",         help="directory path where time slices files should be stored",     default="./timeslices")
    parser.add_argument("-np",  "--nodesPath",              help="directory path where raw timeslices nodes should be stored",  default="./nodes")
    parser.add_argument("-ip",  "--imagePath",              help="directory path where rendered images are stored",             default="./images")
    parser.add_argument("-rp",  "--rasterPath",             help="directory path where temporary raster files are stored",      default="/tmp/rasters")

    parser.add_argument("-d",   "--day",                    help="datetime for single-day analysis, format dd.mm.yy",   type=date_wrapper)

    parser.add_argument('-at',  "--analysisType",           help="Type of analysis to be performed. Can be one of 'generateTimeslices', 'visualizeOverview' or 'rasterizeTimeslices'", default="generateTimeslices")

    args = parser.parse_args()
    cacher = Cacher(args.cachePath)

    psql = PostgreSQLSuite()

    df_agents_parking = pd.read_csv(args.csvPath, sep=";", parse_dates=["parkingStartTime", "parkingEndTime", "parkingDuration"])
    df_agents_parking["parkingDuration"] = pd.to_timedelta(df_agents_parking["parkingDuration"])

    startDate = df_agents_parking.parkingStartTime.dt.date.min()
    endDate = df_agents_parking.parkingStartTime.dt.date.max()
    endDate = datetime.date(year=endDate.year, month=endDate.month, day=endDate.day+1) # set endDate to the day after the last dataframe entry, therefore fully including it
    dif: datetime.timedelta = endDate - startDate

    if not args.analysisType or not (args.analysisType in ['generateTimeslices', 'visualizeOverview', 'rasterizeTimeslices']):
        log.error(f"Parameter analysisType is not correctly specified!")
        log.error(f"Please specify analysisType as one of 'generateTimeslices', 'visualizeOverview' or 'rasterizeTimeslices'")
        exit()

    if args.analysisType == 'generateTimeslices':
        if args.day: # timeslice calculation for one day
            log.info(f"Generating timeslices at {args.day}")
            _startDate = args.day
            nodes = generateNodes(df_agents_timespan=df_agents_parking, startDate=_startDate, nodesPath=args.nodesPath)
            timeslices = exportTimeslicedNodes(nodes=nodes,
                                               timeslicesPath=args.timeslicesPath, cacher=cacher,
                                               startDate=_startDate, write_out=False)
        else:
            log.info(f"Generating timeslices from {startDate} to {endDate}")
            for day in range(dif.days): # timeslice calculation for multiple days
                _startDate, _endDate = localize_dates_offset(year=startDate.year, month=startDate.month, day=startDate.day, offset=day)
                nodes = generateNodes(df_agents_timespan=df_agents_parking, startDate=_startDate, nodesPath=args.nodesPath)
                timeslices = exportTimeslicedNodes(nodes=nodes,
                                                   timeslicesPath=args.timeslicesPath, cacher=cacher,
                                                   startDate=_startDate, write_out=False)


    elif args.analysisType == 'visualizeOverview':
        if args.day: # overview visualization for one day
            log.info(f"Visualizing overview at {args.day}")
            startDate = args.day
            endDate = startDate + datetime.timedelta(days=1)
            nodes = generateNodes(df_agents_timespan=df_agents_parking, startDate=startDate, nodesPath=args.nodesPath)
            timeslices = exportTimeslicedNodes(nodes=nodes, timeslicesPath=args.timeslicesPath,
                                               startDate=startDate, cacher=cacher, write_out=False)
            visualizeOverview(timeslices, args.imagePath, startDate, endDate)
        else:
            log.info(f"Visualizing overview from {startDate} to {endDate}")
            for day in range(dif.days): # overview visualization for multiple days
                _startDate, _endDate = localize_dates_offset(year=args.startDate.year, month=args.startDate.month, day=args.startDate.day, offset=day)
                nodes = generateNodes(df_agents_timespan=df_agents_parking, startDate=_startDate, nodesPath=args.nodesPath)
                timeslices = exportTimeslicedNodes(nodes=nodes, timeslicesPath=args.timeslicesPath,
                                                   startDate=_startDate, cacher=cacher, write_out=False)
                visualizeOverview(timeslices, args.imagePath, _startDate, _endDate)


    elif args.analysisType == 'rasterizeTimeslices':
        if not os.path.isdir(args.rasterPath):
            log.warning(f"{args.rasterPath} does not exist, attempting to create folder..")
            os.mkdir(args.rasterPath)

        if args.day: # raster visualization for one day
            log.info(f"Generating rasters at {args.day}")
            _startDate = args.day
            nodes = generateNodes(df_agents_timespan=df_agents_parking, startDate=_startDate, nodesPath=args.nodesPath)
            timeslices = exportTimeslicedNodes(nodes=nodes, timeslicesPath=args.timeslicesPath,
                                               startDate=_startDate, cacher=cacher, write_out=False)

            imagePath = os.path.join(args.imagePath, f"images-{_startDate.strftime('%d.%m.%y')}")
            rasterPath = os.path.join(args.rasterPath, f"rasters-{_startDate.strftime('%d.%m.%y')}")
            rasterizeTimeslices(timeslices, rasterPath=rasterPath, imagePath=imagePath,
                                slice_datetime=_startDate, perform_rasterization=True)
            shutil.rmtree(rasterPath) # delete temporary files
        else: # raster visualization for multiple days
            log.info(f"Generating rasters from {startDate} to {endDate}")
            days = range(dif.days)
            timeslice_range = {}
            for day in days:
                _startDate, _endDate = localize_dates_offset(year=startDate.year, month=startDate.month, day=startDate.day, offset=day)
                nodes = generateNodes(df_agents_timespan=df_agents_parking, startDate=_startDate, nodesPath=args.nodesPath)
                timeslices = exportTimeslicedNodes(nodes=nodes, timeslicesPath=args.timeslicesPath,
                                                   startDate=_startDate, cacher=cacher, write_out=False)

                imagePath = os.path.join(args.imagePath, f"images-{_startDate.strftime('%d.%m.%y')}")
                rasterPath = os.path.join(args.rasterPath, f"rasters-{_startDate.strftime('%d.%m.%y')}")

                timeslice_range[day] = {
                    "timeslices": timeslices,
                    "startTime": _startDate, "endTime": _endDate,
                    "imagePath": imagePath, "rasterPath": rasterPath }

            rasterizeTimesliceMultipleDays(timeslice_range, perform_rasterization=True)