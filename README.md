# Subscribie  - Subscription Website Builder 
#### variable subscription & recurring payments
[![Build Status](https://travis-ci.org/Subscribie/subscribie.svg?branch=master)](https://travis-ci.org/Subscribie/subscribie)

### What does this project do?                                                   

Quickly build a subscription based website, taking variable monthly payments.

- You have a subscription service to sell!
- Each of your packages have unique selling points (USPs)
- Each have a different reoccurring price

Use Subscribie to build your subscription model business & test your market!

# Why is this project useful?                                                    

A lot of the hard work has been done for you. If you're a devloper, you can
impress your clients quickly, if you're a small business owner, you might want
to try the [subscription website hosting service](http://subscriptionwebsitebuilder.co.uk) but you can always host it yourself too.

- Low risk (not very expensive)
- No coding required
- Simple: Just give us your USPs for each service & price
- Upload your pictures
- Choose between Stripe & Gocardless (more coming soon!) 

An abstraction layer for managing variable recurring subscriptions and billing. Abstracts direct debit and token based card payment providers or payment-institutions.

Keywords: subscriptions, payments, PS2, SEPA 

# Docs 

https://subscribie.readthedocs.io

# Demo

https://subscriptionwebsitebuilder.co.uk

# Where can I get more help, if I need it?

Read through the [docs](https://subscribie.readthedocs.io), especially
about the [Jamla
file](https://subscribie.readthedocs.io/en/latest/concepts/concepts.html) 
and comment on the [issue
queue](https://github.com/Subscribie/subscribie/issues)

# Contributing (for development)

```
git clone https://github.com/Subscribie/subscribie.git
cd subscribie
virtualenv venv
source venv/bin/activate
pip install -e .
export FLASK_APP=subscribie
flask run
```

