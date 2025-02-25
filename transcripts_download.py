#!/usr/bin/env python
import requests


def main(c):
    years = list(range(2010, 2025))
    quarters = list(range(1, 5))
    prolouge = "https://discountingcashflows.com/api/transcript/"
    for y in years:
        for q in quarters:
            try:
                url = (
                    '%s%s/Q%s/%s/' % (prolouge, c, q, y))
                r = requests.get(url)
                with open('./transcripts/%s_Q%s_%s' % (c, q, y),
                          'wb') as f:
                    f.write(r.content)
                print('Downloaded: ', url)
            except Exception:
                pass


if __name__ == '__main__':
    main()
