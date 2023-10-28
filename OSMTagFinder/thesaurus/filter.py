# -*- coding: utf-8 -*-
'''
Created on 07.10.2014

@author: Simon Gwerder
'''

class Filter:

    exactKeyFilter = ['name', 'ele', 'comment', 'image', 'symbol', 'deanery', 'jel', 'rating', 'school:FR', 'alt', 'is_in', 'url', 'web',
                      'wikipedia', 'email', 'converted_by', 'phone', 'opening_hours', 'date', 'time', 'collection_times', 'website',
                      'colour', 'fee', 'population', 'access', 'noexit', 'towards', 'bus_routes', 'busline', 'lines', 'type', 'denotation',
                      'CONTINUE', 'continue', 'copyright', 'stop', 'network', 'comment', 'old_name', 'destination', 'brand', 'fax', 'designation',
                      'turn:lanes', 'owner', 'fire_hydrant:city', 'fire_hydrant:street', 'country', 'contact:google_plus', 'note', 'height',
                      'short_name:ru', 'tpuk_ref', 'wikimedia_commons', 'operator', 'source', 'wikidata', 'wikipedia', 'railway:etcs',
                      'de:regionalschluessel', 'de:amtlicher_gemeindeschluessel', 'contact:xing', 'nspn', '_picture_', 'postal_code', 'exit_to',
                      '_waypoint_', 'label', 'branch', 'note', 'phone', 'created_by', 'start_date', 'end_date', 'description', 'description:ru',
                      'lacounty:bld_id', 'lacounty:ain', 'uir_adr:ADRESA_KOD', 'nysgissam:nysaddresspointid', 'nycdoitt:bin', 'at_bev:addr_date',
                      'raba:id', 'AlpinRes_ID', 'pmfsefin:idedif', 'maaamet:ETAK', 'dibavod:id', 'fid', 'ssr:stedsnr', 'utahagrc:parcelid']

    prefixKeyFilter = ['name:', 'note:', 'alt_name', 'int_name', 'loc_name', 'not:name', 'nat_name', 'official_name', 'short_name', 'reg_name', 'sorting_name',
                       'contact:', 'addr', 'icao', 'iata', 'onkz', 'is_in', 'fixme', 'seamark:fixme', 'wikipedia:',
                       'ois:fixme', 'todo', 'type:', 'admin_level', 'AND_', 'AND:', 'seamark:', 'attribution', 'openGeoDB', 'ref', 'source_ref', 'tiger',
                       'yh:', 'ngbe:', 'gvr:code', 'old_ref_legislative', 'sl_stop_id', 'ele:', 'source:', 'gtfs:',
                       'osak:', 'kms', 'gnis:', 'nhd', 'chicago:building_id', 'hgv', 'nhs', 'ncat', 'nhd-shp:', 'osmc:', 'kp',
                       'int_name', 'CLC:', 'naptan:', 'building:ruian:', 'massgis:', 'WroclawGIS:', 'ref:FR:FANTOIR', 'rednap:', 'ts_', 'type:FR:FINESS',
                       'route_ref', 'lcn_ref', 'ncn_ref', 'rcn', 'rwn_ref', 'old_ref', 'prow_ref', 'local_ref', 'loc_ref', 'reg_ref', 'url',
                       'nat_ref', 'int_ref', 'uic_ref', 'asset_ref', 'carriageway_ref', 'junction:ref', 'fhrs:', 'osmc:', 'cep', 'protection_title',
                       'bag:extract', 'ref:bagid', 'adr_les', 'bag:', 'fresno_', 'uuid', 'uic_name', 'gtfs_id', 'USGS-LULC:', 'reg_', 'IBGE:',
                       'sagns_id', 'protect_id', 'PMSA_ref', 'destination:', 'EH_ref', 'rtc_rate', 'cyclestreets_id', 'woeid', 'CEMT',
                       'depth:dredged', 'GNS:', 'gns:', 'gns_']

    exactValueFilter = []

    prefixValueFilter = []

    def completeFilterList(self):
        '''Merges and returns the exact and prefix filter list'''
        return self.exactKeyFilter + list(set(self.prefixKeyFilter) - set(self.exactKeyFilter))

    def hasKey(self, strKey):
        ''' Checks if 'strKey' is in any key filter list'''
        return self.hasKeyExact(strKey) or self.hasKeyPrefix(strKey)

    def hasKeyExact(self, strKey):
        return strKey in self.exactKeyFilter

    def hasKeyPrefix(self, strKey):
        '''Checks if 'strKey' is in prefixKeyFilter list.'''
        for pkf in self.prefixKeyFilter:
            lowStrKey = strKey.lower()
            lowKeyFilter = pkf.lower()
            if(lowStrKey.startswith(lowKeyFilter)):
                return True
        return False

    def hasValue(self, strValue):
        ''' Checks if 'strValue' is in any key filter list'''
        return self.hasValueExact(strValue) or self.hasValuePrefix(strValue)

    def hasValueExact(self, strValue):
        return strValue in self.exactValueFilter

    def hasValuePrefix(self, strValue):
        '''Checks if 'strValue' is in prefixValueFilter list.'''
        for pvf in self.prefixValueFilter:
            lowStrValue = strValue.lower()
            lowValueFilter = pvf.lower()
            if(lowStrValue.startswith(lowValueFilter)):
                return True
        return False



