import argparse
from arbitrade.main_controller import Controller

def main(params):
    controller = Controller(**params)
    controller.main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-a", "--assets", 
                        type=lambda s: tuple(tuple(asset.split(",")) for asset in s.split(" ")), 
                        help="whitespace delimited input of 'symbol,kind symbol,kind'")
    parser.add_argument("-d", "--date", type=str, help="Datetime format 'YYYYMMDD HH:MM:SS'")
    args = parser.parse_args()
    main({"tm":args.date, "assets":args.assets})