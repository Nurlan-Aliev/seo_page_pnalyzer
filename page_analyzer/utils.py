def build_parts(to_dick, url):

    for i in url:
        if i:
            to_dick['sc'] = i.get('status_code')
            to_dick['created_at'] = i.get('created_at')

        return to_dick
    return to_dick
