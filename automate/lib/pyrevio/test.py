from revio import RevClient

rev = RevClient()
inventory = rev.getInventoryItem('2036898387')

#for record in inventory['records']:
#    customer = rev.getCustomerProfile(record['customer_id'])
#    print(customer['customer_id'], customer['billing_address']['company_name'])
for field in inventory['records']:
    print(field['fields'])
