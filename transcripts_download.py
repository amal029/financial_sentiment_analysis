#!/usr/bin/env python
import requests
# import time


def main():
    years = list(range(2010, 2025))
    quarters = list(range(1, 5))
    consumer_staples = [
        # "ADM",                  # done
        # "BF.B",                 # done
        # "BG",                   # done
        # "CAG",                  # done
        # "CHD",                  # done
        # "CL",                   # done
        # "CLX",                  # done
        # "COST",                 # done
        # "CPB",                  # done
        # "DG",                   # done
        # "DLTR",                 # done
        # "EL",                   # done
        # "GIS",                  # done
        # "HRL",                  # done
        # "HSY",                  # done
        # "K",                    # done
        # "KDP",                  # done
        # "KHC",                  # done
        # "KMB",                  # done
        # "KO",                   # done
        # "KR",                   # done
        # "KVUE",
        # "LW",
        # "MDLZ",
        # "MKC",
        # "MNST",
        # "MO",
        # "PEP",
        # "PG",
        # "PM",
        # "SJM",
        # "STZ",
        # "SYY",
        # "TAP",
        # "TGT",
        # "TSN",
        # "WBA",
        # "WMT"
    ]
    prolouge = "https://discountingcashflows.com/api/transcript/"
    for c in consumer_staples:
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
