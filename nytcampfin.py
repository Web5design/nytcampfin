"""
A Python client for the New York Times Campaign Finance API
"""
__author__ = "Derek Willis (dwillis@gmail.com)"
__version__ = "0.2.0"

import os
import requests
import requests_cache

__all__ = ('NytCampfin', 'NytCampfinError', 'NytNotFoundError')

DEBUG = False

CURRENT_CYCLE = 2012

API_KEY = os.environ['NYT_CAMPFIN_API_KEY']

requests_cache.configure(expire_after=5)

# Error classes

class NytCampfinError(Exception):
    """
    Exception for New York Times Congress API errors
    """

class NytNotFoundError(NytCampfinError):
    """
    Exception for things not found
    """

# Clients

class Client(object):
        
    BASE_URI = "http://api.nytimes.com/svc/elections/us/v3/finances"
    
    def __init__(self, apikey=API_KEY):
        self.apikey = apikey
    
    def fetch(self, path, *args, **kwargs):
        if not kwargs['offset']:
            kwargs['offset'] = 0
        parse = kwargs.pop('parse', lambda r: r['results'][0])
        kwargs['api-key'] = self.apikey

        if not path.lower().startswith(self.BASE_URI):
            url = self.BASE_URI + "%s.json" % path
            url = (url % args)
        else:
            url = path + '?'
        
        resp = requests.get(url, params = dict(kwargs))
        if not resp.status_code in (200, 304):
            content = resp.json
            errors = '; '.join(e for e in content['errors'])
            if resp.status_code == 404:
                raise NytNotFoundError(errors)
            else:
                raise NytCampfinError(errors)
        
        result = resp.json
        
        if callable(parse):
            result = parse(result)
            if DEBUG:
                result['_url'] = url
        return result

class FilingsClient(Client):
    
    def today(self, cycle=CURRENT_CYCLE, offset=0):
        "Returns today's FEC electronic filings"
        path = "/%s/filings"
        result = self.fetch(path, cycle, offset=offset, parse=lambda r: r['results'])
        return result
    
    def date(self, year, month, day, cycle=CURRENT_CYCLE, offset=0):
        "Returns electronic filings for a given date"
        path = "/%s/filings/%s/%s/%s"
        result = self.fetch(path, cycle, year, month, day, offset=offset, parse=lambda r: r['results'])
        return result
    
    def form_types(self, cycle=CURRENT_CYCLE, offset=0):
        "Returns an array of filing form types"
        path = "/%s/filings/types"
        result = self.fetch(path, cycle, offset=offset, parse=lambda r: r['results'])
        return result
        
    def by_type(self, form_type, cycle=CURRENT_CYCLE, offset=0):
        "Returns an array of electronic filings for a given form type"
        path = "/%s/filings/types/%s"
        result = self.fetch(path, cycle, form_type, offset=offset, parse=lambda r: r['results'])
        return result        
    
    def amendments(self, cycle=CURRENT_CYCLE, offset=0):
        "Returns an array of recent amendments"
        path = "/%s/filings/amendments"
        result = self.fetch(path, cycle, offset=offset, parse=lambda r: r['results'])
        return result

class CandidatesClient(Client):
    
    def latest(self, cycle=CURRENT_CYCLE, offset=0):
        "Returns newly registered candidates"
        path = "/%s/candidates/new"
        result = self.fetch(path, cycle, offset=offset, parse=lambda r: r['results'])
        return result
        
    def get(self, cand_id, cycle=CURRENT_CYCLE, offset=0):
        "Returns details for a single candidate within a cycle"
        path = "/%s/candidates/%s"
        result = self.fetch(path, cycle, cand_id, offset=offset)
        return result

    def filter(self, query, cycle=CURRENT_CYCLE, offset=0):
        "Returns a list of candidates based on a search term"
        path = "/%s/candidates/search"
        result = self.fetch(path, cycle, query=query, offset=offset, parse=lambda r: r['results'])
        return result
    
    def leaders(self, category, cycle=CURRENT_CYCLE, offset=0):
        "Returns a list of leading candidates in a given category"
        path = "/%s/candidates/leaders/%s"
        result = self.fetch(path, cycle, category, offset=offset, parse=lambda r: r['results'])
        return result
    
    def seats(self, state, chamber=None, district=None, cycle=CURRENT_CYCLE, offset=0):
        "Returns an array of candidates for seats in the specified state and optional chamber and district"
        if district:
            path = "/%s/seats/%s/%s/%s"
            result = self.fetch(path, cycle, state, chamber, district, offset=offset, parse=lambda r: r['results'])
        elif chamber:
            path = "/%s/seats/%s/%s"
            result = self.fetch(path, cycle, state, chamber, offset=offset, parse=lambda r: r['results'])
        else:
            path = "/%s/seats/%s"
            result = self.fetch(path, cycle, state, offset=offset, parse=lambda r: r['results'])
        return result

class CommitteesClient(Client):
    
    def latest(self, cycle=CURRENT_CYCLE, offset=0):
        "Returns newly registered committees"
        path = "/%s/committees/new"
        result = self.fetch(path, cycle, offset=offset, parse=lambda r: r['results'])
        return result
    
    def get(self, cmte_id, cycle=CURRENT_CYCLE, offset=0):
        "Returns details for a single committee within a cycle"
        path = "/%s/committees/%s"
        result = self.fetch(path, cycle, cmte_id, offset=offset)
        return result
    
    def filter(self, query, cycle=CURRENT_CYCLE, offset=0):
        "Returns a list of committees based on a search term"
        path = "/%s/committees/search"
        result = self.fetch(path, cycle, query=query, offset=offset, parse=lambda r: r['results'])
        return result

    def filings(self, cmte_id, cycle=CURRENT_CYCLE, offset=0):
        "Returns a list of a committee's filing within a cycle"
        path = "/%s/committees/%s/filings"
        result = self.fetch(path, cycle, cmte_id, offset=offset, parse=lambda r: r['results'])
        return result

    def contributions(self, cmte_id, cycle=CURRENT_CYCLE, offset=0):
        "Returns a list of a committee's contributions within a cycle"
        path = "/%s/committees/%s/contributions"
        result = self.fetch(path, cycle, cmte_id, offset=offset, parse=lambda r: r['results'])
        return result

    def contributions_to_candidate(self, cmte_id, candidate_id, cycle=CURRENT_CYCLE, offset=0):
        "Returns a list of a committee's contributions to a given candidate within a cycle"
        path = "/%s/committees/%s/contributions/candidates/%s"
        result = self.fetch(path, cycle, cmte_id, candidate_id, offset=offset, parse=lambda r: r['results'])
        return result
        
    def leadership(self, cycle=CURRENT_CYCLE, offset=0):
        "Returns a list of leadership committees"
        path = "/%s/committees/leadership"
        result = self.fetch(path, cycle, offset=offset, parse=lambda r: r['results'])
        return result

class NytCampfin(Client):
    """
    Implements the public interface for the NYT Campaign Finance API

    Methods are namespaced by topic (though some have multiple access points).
    Everything returns decoded JSON, with fat trimmed.

    In addition, the top-level namespace is itself a client, which
    can be used to fetch generic resources, using the API URIs included
    in responses. This is here so you don't have to write separate
    functions that add on your API key and trim fat off responses.

    Create a new instance with your API key, or set an environment
    variable called NYT_CAMPFIN_API_KEY.

    NytCampfin uses requests and the requests-cache library. By default,
    it uses a sqlite database named cache.sqlite, but other cache options
    may be used.
    """

    def __init__(self, apikey=os.environ.get('NYT_CAMPFIN_API_KEY')):
        super(NytCampfin, self).__init__(apikey)
        self.filings = FilingsClient(self.apikey)
        self.committees = CommitteesClient(self.apikey)
        self.candidates = CandidatesClient(self.apikey)
        
        

