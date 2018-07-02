import yaml, flask_login

class Jamla():

    jamla = None

    def load(self, src='example.yaml'):
        with open(src, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
        for section in cfg:
            print (section)
        self.jamla = cfg
        return cfg

    def sku_exists(self, sku):
	for item in self.jamla['items']:
	    if item['sku'] == str(sku):
		return True
	return False
    def sku_get_index(self, sku):
	for index,v in enumerate(self.jamla['items']):
	    if self.jamla['items'][index]['sku'] == str(sku):
		return index
	return False

    def requires_subscription(self, sku):
        index = self.sku_get_index(sku)
        return bool(self.jamla['items'][index]['requirements']['subscription'])

    def requires_instantpayment(self, sku):
        index = self.sku_get_index(sku)
        return bool(self.jamla['items'][index]['requirements']['instant_payment'])

    def sku_get_title(self, sku):
	index = self.sku_get_index(sku)
	title  = self.jamla['items'][index]['title']
	return title

    def sku_get_monthly_price(self, sku):
	price = self.jamla['items'][self.sku_get_index(sku)]['monthly_price']
	return price
    def sku_get_upfront_cost(self, sku):
	sell_price = self.jamla['items'][self.sku_get_index(sku)]['sell_price']
	return sell_price

    def get_primary_icons(self, jamla=None):
        """ Returns list of all static file paths """
        if jamla is None:
            raise Exception("get_primary_icons expects a jamla object")
        icons = []
        for item in self.jamla['items']:
            if item['primary_icon']['src']:
                icons.append(item['primary_icon']['src'])
        return icons

    def get_selling_points(self, sku):
	selling_points = self.jamla['items'][self.sku_get_index(sku)]['selling_points']
	return selling_points

    def has_connected(self, service):
	if service == 'gocardless':
	    try:
		# May exist is flask session if jamla hasn't reloaded yet
		flask_login.current_user.gocardless_access_token
	    except AttributeError:
		pass
	    # May have already been loaded from file is instance has been stated
	    # with access_token token already present
	    access_token = self.jamla['payment_providers']['gocardless']['access_token']
	    if access_token is not None and len(access_token) > 0:
		return True
	if service == 'stripe':
	    try:
		# May exist is flask session if jamla hasn't reloaded yet
		flask_login.current_user.stripe_publishable_key
	    except AttributeError:
		pass
	    # May have already been loaded from file is instance has been stated
	    # with access_token token already present
	    publishable_key= self.jamla['payment_providers']['stripe']['publishable_key']
	    if publishable_key is not None and len(publishable_key) > 0:
		return True
	    return False

    def get_secret(self, service, name):
	if service == 'gocardless' and name == 'access_token':
	    if self.has_connected('gocardless'):
		try:
		    return flask_login.current_user.gocardless_access_token
		except AttributeError:
		    pass
		try:
		    return self.jamla['payment_providers']['gocardless']['access_token']
		except Exception:
		    pass
		try:
		    return app.config['GOCARDLESS_TOKEN']
		except Exception:
		    pass
