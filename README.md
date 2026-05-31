# Checkout-system
Checkout system or POS system for our little store


Setup (one-time)

Create a product database.
For each product store:
Barcode
Name
Price
Stock

Cashier opens checkout

Start with an empty cart.
Wait for barcode scan.

When a barcode is scanned

Receive barcode number.
Search database for matching barcode.
If found:
Add product to cart.
If already in cart, increase quantity.
Update total.
If not found:
Show "Product not found".

Repeat until customer is done shopping.

When customer clicks Pay

Calculate total.
Ask payment method:
Cash
Card

If cash:
Enter amount received.
Calculate change.
Show change.

If card:
Show total amount.
Cashier enters same amount into PAX terminal.
Customer pays.
Confirm payment succeeded.

Complete sale

Save sale record.
Save all items sold.
Reduce stock for each product.
Print receipt (optional).
Clear cart.
Ready for next customer.

Admin side

Add product
Enter barcode.
Enter name.
Enter price.
Enter stock.
Save.

Edit product

Search product.
Change details.
Save.

Restock

Select product.
Add quantity.
Save.
