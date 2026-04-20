def get_base_url(website_name):
    base = website_name.rstrip('/')

    if '/en/' in base:
        base = base.split('/en/')[0]
    elif '/ar/' in base:
        base = base.split('/ar/')[0]
    elif '/fr/' in base:
        base = base.split('/fr/')[0]  
    elif base.endswith('/en') or base.endswith('/ar') or base.endswith('/fr'):
        base = base[:-3]
    else:
        if 'pantheonsite.io' in base:
            base = base.split('.io')[0] + '.io'
        else:
            base = base.split('.com')[0] + '.com'
        return base.rstrip('/')

    return base.rstrip('/')

def slugify_url(text):

    url = str(text).strip()
    if 'pantheonsite.io' in url:
        url = url.split('.io')[-1]
    else:
        url = url.split('.com')[-1]

    
    url = url.strip('/')
    return f'/{url}'

def slugify_alias(text, redirection=False, path_url_slug=False, path_to_slug=False):
    alias = str(text).strip()
    if 'pantheonsite.io' in alias:
        alias = alias.split('.io')[-1]
    else:
        alias = alias.split('.com')[-1]

    if not redirection:
        if alias.startswith('/en/') or alias.startswith('/ar/') or alias.startswith('/fr/'):
            return alias[3:]
        else:
            return alias[3:]
    else:
        
        if path_url_slug:
           return alias.strip('/')
        
        elif path_to_slug:
            if alias:
                return alias
            else:
                return '/'    
            
            
                