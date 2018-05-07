import yaml

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
	    if jamla['items'][index]['sku'] == str(sku):                             
		return index                                                         
	return False                                                                 
										     
    def sku_get_title(self, sku):                                                          
	index = sku_get_index(sku)                                                   
	title  = self.jamla['items'][index]['title']                                      
	return title                                                                 
										     
    def sku_get_monthly_price(self, sku):                                                  
	price = self.jamla['items'][sku_get_index(sku)]['monthly_price']                  
	return price

    def get_primary_icons(self, jamla=None):
        """ Returns list of all static file paths """
        if jamla is None:
            raise Exception("get_primary_icons expects a jamla object")
        icons = []
        for item in self.jamla['items']:
            if item['primary_icon']['src']:
                icons.append(item['primary_icon']['src'])
        return icons

