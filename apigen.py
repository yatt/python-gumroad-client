print '######################'
print '# generated code'
print '######################'
for line in open('apidef.txt'):
    line = line.strip()
    sp = line[1:].replace('/:', '__').split()

    params = sp[2:]
    http_method = sp[1]
    method_name = sp[0] + '_' + sp[1]
    url = "'" + line.split()[0] + "'"
    url = url if ':id' not in url else url.replace(':id', '') +  " + kwargs['id']"
    print """def %s(self, **kwargs):
    return self._open('%s', %s, **kwargs)
    """ % (method_name, http_method, url)
print '######################'
