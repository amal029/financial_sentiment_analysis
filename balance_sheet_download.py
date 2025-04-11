#!/usr/bin/env python
import requests
import pandas as pd
# import os


def mainbalancesheet(c):
    p = "discountingcashflows.com/api/balance-sheet-statement/quarterly/"
    try:
        url = ('https://%s%s/' % (p, c))
        r = requests.get(url)
        with open('./balance_sheets/%s.json' % c, 'wb') as f:
            f.write(r.content)
            print('Downloaded: ', url)
    except Exception:
        pass


def maincashflow(c):
    p = "discountingcashflows.com/api/cash-flow-statement/quarterly/"
    try:
        url = ('https://%s%s/' % (p, c))
        r = requests.get(url)
        with open('./cash_flow/%s.json' % c, 'wb') as f:
            f.write(r.content)
            print('Downloaded: ', url)
    except Exception:
        pass


def mainratios(c):
    p = "discountingcashflows.com/api/ratios/quarterly/"
    try:
        url = ('https://%s%s/' % (p, c))
        r = requests.get(url)
        with open('./ratios/%s.json' % c, 'wb') as f:
            f.write(r.content)
            print('Downloaded: ', url)
    except Exception:
        pass


def mainprices(c):
    p = "discountingcashflows.com/api/prices/daily/"
    try:
        url = ('https://%s%s/' % (p, c))
        r = requests.get(url)
        with open('./prices_daily/%s.json' % c, 'wb') as f:
            f.write(r.content)
            print('Downloaded: ', url)
    except Exception:
        pass


if __name__ == '__main__':
    sp500 = [x.strip() for x in list(pd.read_csv('sp500.csv')['Symbol'])]

    # XXX: Done
    # files = [f.split('.json')[0]
    #          for f in os.listdir('./balance_sheets/')
    #          if os.path.isfile(os.path.join('./balance_sheets/', f))]

    # for c in sp500:
    #     if c in files:
    #         continue
    #     mainbalancesheet(c)
    #     files.append(c)

    # XXX: Done
    # files = [f.split('.json')[0]
    #          for f in os.listdir('./cash_flow/')
    #          if os.path.isfile(os.path.join('./cash_flow/', f))]

    # for c in sp500:
    #     if c in files:
    #         continue
    #     maincashflow(c)
    #     files.append(c)

    # XXX: Done
    # files = [f.split('.json')[0]
    #          for f in os.listdir('./ratios/')
    #          if os.path.isfile(os.path.join('./ratios/', f))]

    # for c in sp500:
    #     if c in files:
    #         continue
    #     mainratios(c)
    #     files.append(c)

    # files = [f.split('.json')[0]
    #          for f in os.listdir('./prices_daily/')
    #          if os.path.isfile(os.path.join('./prices_daily/', f))]

    # for c in sp500:
    #     if c in files:
    #         continue
    #     mainprices(c)
    #     files.append(c)
