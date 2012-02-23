#! /usr/bin/python2.7
# coding: utf-8
__author__ = 'yatt/brainfs'
__mail__ = 'darknesssharp@gmail.com'
__version__ = '0.0.1'
__license__ = 'MIT'
# ref: https://gumroad.com/api/authentication
#
# # sample
# # setup background interface
# api = Gumroad('email', 'password')
# api.login()
# GumroadItem._api = api
# 
# # create new item
# item = GumroadItem(name = 'foo', price = 100, description = '')
# item.update() 
# 
# # update item
# item = GumroadItem(id = 12)
# item.name = 'bar'
# item.update()
# 
# # delete item
# item = GumroadItem(id = 10)
# item.delete()
#
# api.logout()
#
import urllib
import urllib2
import base64
import json

class GumroadException(Exception):
    def __init__(self, type, message):
        self.type = type
        self.message = message
    def __str__(self):
        if self.type:
            return '%s : %s' % (self.type, self.message)
        else:
            return self.message

class Gumroad(object):
    def __init__(self, email, password):
        self.account = {'email': email, 'password': password}
        self.token = None # authentication token
        self.opener = urllib2.build_opener()
    def _link(self, path):
        return 'https://gumroad.com/api/v1' + path
    def _open(self, method, path, **kwargs):
        # parameter
        q = lambda s: urllib.quote(s, '')
        qq = lambda s: urllib.quote(s, '~')
        for key in kwargs:
             value = kwargs[key]
             if isinstance(value, unicode):
                 kwargs[key] = value.encode('utf-8')
             else:
                 kwargs[key] = str(value)
        data = '&'.join('%s=%s' % (q(k), qq(kwargs[k])) for k in kwargs)

        # create request
        url = self._link(path)
        req = urllib2.Request(url, data)
        req.get_method = (lambda m: lambda: m)(method.upper())

        # attach token to request
        if self.token:
            encoded = base64.b64encode(self.token + ':')
            req.add_header('Authorization', 'Basic ' + encoded)
        
        # request
        try:
            conn = self.opener.open(req)
            cont = conn.read()
            jsondoc = json.loads(cont)
            # error handling
            if jsondoc['success'] is False:
                err = jsondoc['error']
                type = err.get('type', '')
                msg = err.get('message', '')
                raise GumroadException(type, msg)
            return jsondoc
        except Exception, e:
            raise e
            
    def login(self):
        doc = self.sessions_post(**self.account)
        self.token = doc['token']
    def logout(self):
        self.sessions_delete(**self.account)
        self.token = None
    
    ######################
    # generated code
    ######################
    def sessions_post(self, **kwargs):
        return self._open('post', '/sessions', **kwargs)
    def sessions_delete(self, **kwargs):
        return self._open('delete', '/sessions', **kwargs)
    def links_post(self, **kwargs):
        return self._open('post', '/links', **kwargs)
    def links_get(self, **kwargs):
        return self._open('get', '/links', **kwargs)
    def links__id_get(self, **kwargs):
        return self._open('get', '/links/' + kwargs['id'], **kwargs)
    def links__id_put(self, **kwargs):
        return self._open('put', '/links/' + kwargs['id'], **kwargs)
    def links__id_delete(self, **kwargs):
        return self._open('delete', '/links/' + kwargs['id'], **kwargs)
    ######################

class GumroadItem(object):
    _api = None
    @staticmethod
    def setapi(api):
        GumroadItem._api = api

    def __init__(self, **kwargs):
        for k in kwargs:
            self.__dict__[k] = kwargs[k]
        if self.id is not None:
            self.initbyid()
    def initbyid(self):
       doc = GumroadItem._api.links__id_get(id = self.id)
       for k in self.__dict__:
           self.__dict__[k] = doc['link'][k]
    def update(self):
        if self.id is None:
            doc = GumroadItem._api.links_post(**self.__dict__)
            self.id = doc['link']['id']
            self.initbyid()
        else:
            return GumroadItem._api.links__id_put(**self.__dict__)
    def delete(self):
        return GumroadItem._api.links__id_delete(id = self.id)
    @staticmethod
    def all():
        doc = GumroadItem._api.links_get()
        return map(lambda kwargs: GumroadItem(**kwargs), doc['links'])
