from revio import RevClient

rev = RevClient()
inventory = rev.getInventoryItem('2036898387')

for record in inventory['records']:
    customer = rev.getCustomerProfile(40549)
    print(customer['billing_address']['company_name'])

