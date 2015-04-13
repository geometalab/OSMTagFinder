# -*- coding: utf-8 -*-

'''
Created on 13.04.2015
Functions to access the Microsoft Translator API HTTP Interface, using python's urllib/urllib2 libraries
http://denis.papathanasiou.org/2012/05/07/using-microsofts-translator-api-with-python/
Microsoft Konto: osmtagfinder@hotmail.com - #T0P#SECRET# (see access token there)
2 Billion requests per month.
 
@author:  Denis Papathanasiou
'''

import urllib, urllib2
import json
import xml.etree.ElementTree as ET

from datetime import datetime

class MicrosoftTranslator:
    
    clientID = "osmtagfinder"
    clientSecret = "#T0P#SECRET##T0P#SECRET#"
    
    def datestring (self, display_format="%a, %d %b %Y %H:%M:%S", datetime_object=None):
        """Convert the datetime.date object (defaults to now, in utc) into a string, in the given display format"""
        if datetime_object is None:
            datetime_object = datetime.utcnow()
        return datetime.strftime(datetime_object, display_format)
    
    def getAccessToken (self, client_id=None, client_secret=None):
        """Make an HTTP POST request to the token service, and return the access_token,
        as described in number 3, here: http://msdn.microsoft.com/en-us/library/hh454949.aspx
        """
        if not client_id:
            client_id = self.clientID
            
        if not client_secret:
            client_secret = self.clientSecret
    
        data = urllib.urlencode({
                'client_id' : client_id,
                'client_secret' : client_secret,
                'grant_type' : 'client_credentials',
                'scope' : 'http://api.microsofttranslator.com'
                })
    
        try:
    
            request = urllib2.Request('https://datamarket.accesscontrol.windows.net/v2/OAuth2-13')
            request.add_data(data) 
    
            response = urllib2.urlopen(request)
            response_data = json.loads(response.read())
    
            if response_data.has_key('access_token'):
                return response_data['access_token']
    
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print self.datestring(), 'Could not connect to the server:', e.reason
            elif hasattr(e, 'code'):
                print self.datestring(), 'Server error: ', e.code
        except TypeError:
            print self.datestring(), 'Bad data from server'
    
    supportedLanguages = { # as defined here: http://msdn.microsoft.com/en-us/library/hh456380.aspx
        'ar' : ' Arabic',
        'bg' : 'Bulgarian',
        'ca' : 'Catalan',
        'zh-CHS' : 'Chinese (Simplified)',
        'zh-CHT' : 'Chinese (Traditional)',
        'cs' : 'Czech',
        'da' : 'Danish',
        'nl' : 'Dutch',
        'en' : 'English',
        'et' : 'Estonian',
        'fi' : 'Finnish',
        'fr' : 'French',
        'de' : 'German',
        'el' : 'Greek',
        'ht' : 'Haitian Creole',
        'he' : 'Hebrew',
        'hi' : 'Hindi',
        'hu' : 'Hungarian',
        'id' : 'Indonesian',
        'it' : 'Italian',
        'ja' : 'Japanese',
        'ko' : 'Korean',
        'lv' : 'Latvian',
        'lt' : 'Lithuanian',
        'mww' : 'Hmong Daw',
        'no' : 'Norwegian',
        'pl' : 'Polish',
        'pt' : 'Portuguese',
        'ro' : 'Romanian',
        'ru' : 'Russian',
        'sk' : 'Slovak',
        'sl' : 'Slovenian',
        'es' : 'Spanish',
        'sv' : 'Swedish',
        'th' : 'Thai',
        'tr' : 'Turkish',
        'uk' : 'Ukrainian',
        'vi' : 'Vietnamese',
    }
    
    def printSupportedLanguages (self):
        """Display the list of supported language codes and the descriptions as a single string
        (used when a call to translate requests an unsupported code)"""
    
        codes = []
        for k,v in self.supportedLanguages.items():
            codes.append('\t'.join([k, '=', v]))
        return '\n'.join(codes)
    
    def toBytestring (self, s):
        """Convert the given unicode string to a bytestring, using utf-8 encoding,
        unless it's already a bytestring"""
    
        if s:
            if isinstance(s, str):
                return s
            else:
                return s.encode('utf-8')
    
    def translate (self, text, toLang, fromLang=None, access_token=None):
        """Use the HTTP Interface to translate text, as described here:
        http://msdn.microsoft.com/en-us/library/ff512387.aspx
        and return a string if successful
        """
        access_token = self.getAccessToken()
        if not access_token:
            print 'Sorry, the access token is invalid'
        else:
            if toLang not in self.supportedLanguages.keys():
                print 'Sorry, the API cannot translate to', toLang
                print 'Please use one of these instead:'
                print self.printSupportedLanguages()
            else:
                data = { 'text' : self.toBytestring(text), 'to' : toLang }
    
                if fromLang:
                    if fromLang not in self.supportedLanguages.keys():
                        print 'Sorry, the API cannot translate from', fromLang
                        print 'Please use one of these instead:'
                        print self.printSupportedLanguages()
                        return
                    else:
                        data['from'] = fromLang
    
                try:
                    request = urllib2.Request('http://api.microsofttranslator.com/v2/Http.svc/Translate?'+urllib.urlencode(data))
                    request.add_header('Authorization', 'Bearer '+access_token)
    
                    response = urllib2.urlopen(request)
                    xml = response.read()
                    return self.getTextFromMsmtXml(xml)
                
                except urllib2.URLError, e:
                    if hasattr(e, 'reason'):
                        print self.datestring(), 'Could not connect to the server:', e.reason
                    elif hasattr(e, 'code'):
                        print self.datestring(), 'Server error: ', e.code
                    return None
                        
                        
    def getTextFromMsmtXml (self, xml):
        """Parse the xml string returned by the MS machine translation API, and return just the text"""
        doc = ET.fromstring(xml)
        return doc.text
#         text = []
#         for elem in doc:
#             print str(elem)
#             if elem.text:
#                 elem_text = ' '.join(elem.text.split())
#                 if len(elem_text) > 0:
#                     text.append(elem_text)
#         
#         return ' '.join(text)
    
    
if __name__ == '__main__':
    mt = MicrosoftTranslator()
    print str(mt.translate('Uhr', 'en'))
    
    
