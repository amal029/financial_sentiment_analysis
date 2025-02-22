#!/usr/bin/env python
import requests
# import time


def main():
    years = list(range(2010, 2025))
    quarters = list(range(1, 5))
    utilities = [
        # 'AEE',                  # done
        # 'AEP',                  # done
        # 'AES',                  # done
        # 'ATO',                  # done
        # 'AWK',                  # done
        # 'CEG',                  # done
        # 'CMS',                  # done
        # 'CNP',                  # done
        # 'D',                    # done
        # 'DTE',                  # done
        # 'DUK',                  # done
        # 'ED',                   # done
        # 'EIX',                  # done
        # 'ES',                   # done
        # 'ETR',                  # done
        # 'EVRG',                 # done
        # 'EXC',                  # done
        # 'FE',                   # done
        # 'LNT',                  # done
        # 'NEE',                  # done
        # 'NI',                   # done
        # 'NRG',                  # done
        # 'PCG',                  # done
        # 'PEG',                  # done
        # 'PNW',                  # done
        # 'PPL',                  # done
        # 'SO',                   # done
        # 'SRE',                  # done
        # 'VST',                  # done
        # 'WEC',                  # done
        # 'XEL'                   # done
    ]
    prolouge = "https://discountingcashflows.com/api/transcript/"
    for c in utilities:
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
        # time.sleep(120)         # sleep for 2 minutes


if __name__ == '__main__':
    main()
