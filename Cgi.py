# evil presentations CGI interface
#
# Copyright (C) 2008 James Aylett

"""
evilpresentations' CGI driver.
"""

import Flickr, cgi, cgitb, os, time, urllib
from jinja import Template, Context, FileSystemLoader

assets_version = 2

class CgiError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def quote_pro(s):
    s = s.replace('/', '__')
    s = urllib.quote_plus(s)
    return s

def unquote_pro(s):
    s = s.replace('__', '/')
    return urllib.unquote_plus(s)

class Driver:
    """evilpresentations' CGI driver; initialise with a Flickr object."""
    def __init__(self, flickr, install_dir):
        """Initialise driver."""
        self.flickr = flickr
        self.install_dir = install_dir

    def process_request(self):
        """Process an HTTP request."""
        cgitb.enable()
        method = os.environ.get('REQUEST_METHOD', 'GET')

        p = os.environ.get('PATH_INFO', '')

        p = p.split('/')
        p = map(lambda x: unquote_pro(x), p)

        if method=='GET':
            self.do_get(p)
        elif method=='POST':
            self.do_post(p)
        else:
            print "Status: 405 No, that ain't gonna work"
            if p[1]=='presentation':
                print "Allow: GET,POST"
            else:
                print "Allow: GET"
            print

    def do_post(self, p):
        """Process a POST request."""

        if p[1]=='presentation':
            self.make_presentation(p[2:])
        else:
            print "Status: 405 Never with POST, pretty boy"
            print "Allow: GET"
            print

    def do_get(self, p):
        """Process a GET request."""

        if p[1]=='presentation':
            self.do_presentation(p[2:])
        else:
            self.do_index()

    def do_index(self):
        tmpl = Template('index', FileSystemLoader(self.install_dir))
        c = Context({'assetpath': '/assets/%i' % assets_version})
        print "Content-Type: text/html; charset=utf-8"
        print
        print tmpl.render(c).encode('utf-8')

    def _get_photos(self, config=None):
        if config==None:
            config = { 'start': 1, 'middle': 8, 'end': 1, 'order': 'start,middle,end' }

        photos = []
        for type in config.get('order', 'start,middle,end').split(','):
            photos.extend(self.flickr.get_photos(type, config[type]))

        def fixup_photo_array(p):
            photo_uri = 'http://farm%s.static.flickr.com/%s/%s_%s.jpg' % (p[1], p[2], p[0], p[3])
            user_uri = 'http://flickr.com/people/%s/' % p[4]
            res = [photo_uri, user_uri]
            res.extend(p)
            return res

        photos = map(fixup_photo_array, photos)

        return photos

    def _extract_metadata(self, p, read_post_data=False):
        title = u'Presentation'
        presenter = u''
        affiliation = u''

        result = {'title':u'Presentation', 'presenter':u'', 'affiliation': u''}

        if read_post_data:
            form = cgi.FieldStorage(keep_blank_values=False)
            for k in form.keys():
                r =  ", ".join(form.getlist(k))
                if r!='':
                    result[k] = r

        # presenter, affiliation, title are UTF-8 encoded, using
        # RFC 3987 section 3.1 (as I understand it).
        try:
            presenter = p[0].decode('utf-8')
            presenter = presenter.split(';')
            if len(presenter)>1 and presenter[1]!='':
                result['affiliation'] = presenter[1]
            if presenter[0]!='':
                result['presenter'] = presenter[0]
        except IndexError:
            pass
        try:
            r = p[1].decode('utf-8')
            if r!='':
                result['title'] = r
        except IndexError:
            pass
        # FIXME: could allow overriding this in post data
        result['dateline'] = time.strftime('%A %B %d, %Y')

        # If the URI has the order and number of each image type to use,
        # set that up in the metadata dictionary.
        if len(p)>2:
            try:
                if not p[2][0].isdigit():
                    # type/number string of format <type>=<n>;...
                    pbits = p[2].split(';')
                    order = ''
                    for pb in pbits:
                        d = pb.split('=')
                        if len(d)==1:
                            d.append(d[0])
                        if order!='':
                            order = order + ','
                        order = order + d[0]
                        result['images.' + d[0]] = d[1]
                    result['images.order'] = order
                    return result
            except:
                pass

        # If the URI has the actual photos in, use them
        if len(p)>2:
            ps = p[2:]
            photos = []
            for photo in ps:
                pb = photo.split(';')
                if len(pb)!=5:
                    raise CgiError("Look, you can't just make up URIs, okay? There are *rules*.")
                (id, farm, server, secret, owner) = pb
                photo_uri = 'http://farm%s.static.flickr.com/%s/%s_%s.jpg' % (farm, server, id, secret)
                user_uri = 'http://flickr.com/people/%s/' % owner
                photos.append([photo_uri, user_uri, id, farm, server, secret, owner])
            result['photos'] = photos

        return result

    def _get_config_from_metadata(self, metadata):
        config = {}
        for k in metadata.keys():
            if k.startswith('images.'):
                if k=='images.order':
                    config['order'] = metadata[k]
                else:
                    try:
                        config[k[7:]] = int(metadata[k])
                    except ValueError:
                        pass
        if len(config)==0:
            config=None
        return config

    def make_presentation(self, p):
        metadata = self._extract_metadata(p, True)
        config = self._get_config_from_metadata(metadata)
        photos = self._get_photos(config)
        metadata['photos'] = photos

        print "Status: 302 Almost there..."
        print "Location: " + self._make_uri(metadata)
        print

    def _make_uri(self, metadata):
        uri = '/presentation/' + quote_pro(metadata['presenter'])
        uri = uri + ';' + quote_pro(metadata['affiliation'])
        uri = uri + '/' + quote_pro(metadata['title'])
        for photo in metadata['photos']:
            uri += '/' + quote_pro(photo[2]) + ';' + quote_pro(photo[3])
            uri += ';' + quote_pro(photo[4]) + ';' + quote_pro(photo[5])
            uri += ';' + quote_pro(photo[6])
        
        return uri

    def do_presentation(self, p):
        metadata = self._extract_metadata(p)
        if metadata.has_key('photos'):
            cacheable = True
        else:
            metadata['photos'] = self._get_photos(self._get_config_from_metadata(metadata))
            cacheable = False

        credits = []
        src_uris = map(lambda x: x[1], metadata['photos'])
        src_uris.sort()
        for src_uri in src_uris:
            if not src_uri in credits:
                credits.append(src_uri)
        metadata['credits'] = credits
        metadata['assetpath'] = '/assets/%i' % assets_version

        tmpl = Template('presentation', FileSystemLoader(self.install_dir))
        c = Context(metadata)
        print "Content-Type: text/html; charset=utf-8"
        if cacheable:
            print "Cache-Control: max-age=86400" # let it go a day...
        else:
            print "Cache-Control: no-cache, must-revalidate, private"
            print "Pragma: no-cache"
        print
        print tmpl.render(c).encode('utf-8')
