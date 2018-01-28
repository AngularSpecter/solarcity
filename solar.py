import requests
#from lxml import html
import datetime
import json

class SolarCity:

    BASE_URL = 'https://mysolarcity.com/solarcity-api/powerguide/v1.0/'
    MEASUREMENT_URL = BASE_URL + 'measurements/'
    CONSUMPTION_URL = BASE_URL + 'consumption/'

    COSTS_URL  = 'https://mysolarcity.com/solarcity-api/solarbid/api/installation/energycosts/'
    ALERTS_URL = 'https://spa.solarcity.com/api/public/'
    
    auth_token      = None
    persist_token   = None
    include_current = 'true'
    time_period     = 'Hour'
    byDevice        = False
    cookies         = {}
    
    format_string = '%Y-%m-%dT%H:%M:%S'
        
    def __init__( self, guid, token, persistance ):

        self.GUID = guid
        self.TOKEN = token
        self.PERSIST_TOKEN = persistance
        self.cookies[ 'FedAuth' ] = self.TOKEN
        #self.cookies['persistance'] = self.PERSIST_TOKEN

        self.costs = self.get_costs()

    def set_token(self, value ):
        self.TOKEN = value

    def set_period(self, period ):
        if period not in {'QuarterHour', 'Hour', 'Day', 'Month', 'Year' }:
            raise ValueError( period + ' is not a valid type' )
        self.time_period = period

    def build_url(self, start_time, end_time, by_device = None, period = None  ):

        if not by_device: by_device = self.byDevice
        if not period   : period    = self.time_period
        
        URL = self.MEASUREMENT_URL + self.GUID + '?'
        URL += 'StartTime='    + start_time
        URL += '&EndTime='     + end_time
        URL += '&IsByDevice='  + str( by_device )
        URL += '&Period='      + period
        return URL

    def get_costs( self ):
        URL = self.COSTS_URL + self.GUID
        data = requests.get( URL )

        return json.loads( data.text )

    def get_alerts( self ):
        URL = self.ALERTS_URL + self.GUID
        data = requests.get( URL )
        return json.loads( data.text )

        
    def get_today_total( self ):

        try:
            start_time = datetime.date.today()
            end_time   = datetime.date.today() + datetime.timedelta( days=1 ) - datetime.timedelta( minutes=1 )
            #end_time   = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            end_time_str   = end_time.strftime('%Y-%m-%dT%H:%M:%S')

            URL = self.build_url( start_time_str, end_time_str, 'False', 'Hour' )
                           
            reply         = requests.get( URL, cookies = self.cookies )
            data          = json.loads( reply.text )

            if 'persistence' in reply.cookies: self.cookies['persistence'] = reply.cookies['persistence']
      
                
            price  = self.costs['UtilityCostPerkWh']
            energy = data['TotalEnergyInIntervalkWh'] 

            totals = {}
            totals['energy'] = energy
            totals['cost']   = float( energy ) * float( price )

            return totals
        except:
            print( reply.text )
            return None

    def get_month_total( self ):

        try:
            start_time = datetime.date.today().replace(day=1)
            end_time   = datetime.datetime.now()

            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            end_time_str   = end_time.strftime('%Y-%m-%dT%H:%M:%S')

            URL = self.build_url( start_time_str, end_time_str, 'False', 'Day' )
            reply = requests.get( URL, cookies = self.cookies )
            
            if 'persistence' in reply.cookies: self.cookies['persistence'] = reply.cookies['persistence']
            data          = json.loads( reply.text )

            price  = self.costs['UtilityCostPerkWh']
            energy = data['Measurements'][-1]['CumulativekWh']

            totals = {}
            totals['energy'] = energy
            totals['cost']   = float( energy ) * float( price )

            return totals           

        except:
            print( reply.text )
            raise
            return None        

    def get_today( self ):
        start_time = datetime.date.today().strftime('%Y-%m-%dT%H:%M:%S')
        end_time   = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        URL = self.build_url( start_time, end_time )
        payload = {}
        payload[ 'FedAuth' ] = self.TOKEN
        
        print( URL )
        data = requests.get( URL, cookies = payload )
        return json.loads(data.text)
        
    def get_last_hour( self ):
        then = datetime.datetime.now() - datetime.timedelta( hours=1 )
        start_time = then.strftime('%Y-%m-%dT%H:%M:%S') 
        end_time   = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')        

        URL = self.build_url( start_time, end_time )
        payload = {}
        payload[ 'FedAuth' ] = self.TOKEN

        print( URL )
        data = requests.get( URL, cookies = payload )
        return json.loads(data.text)

