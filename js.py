def js_reqs(page='console'):
    from plum.settings import EXTERNAL_JS, D3_JS, PLUGIN_JS, TEMPLATE_VARS, FP_JS, ADMIN_JS
    if page == 'admin':
        to_include = EXTERNAL_JS, D3_JS, PLUGIN_JS, ADMIN_JS
    elif page == 'old':
        to_include = EXTERNAL_JS, PLUGIN_JS, FP_JS_OLD
    else:
        to_include = EXTERNAL_JS, D3_JS, PLUGIN_JS, FP_JS

    js = []
    for i in to_include:
        for ii in i:
            if ii.find('http') == -1:
                ii = TEMPLATE_VARS['JS_URL'] + ii
            js.append(ii)
    return js