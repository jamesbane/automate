from revio import RevClient

rev = RevClient()
inventory = rev.getInventoryItem('8053572512')

for record in inventory['records']:
    customer = rev.getCustomerProfile(record['customer_id'])
    print(customer['customer_id'], customer['billing_address']['company_name'])
