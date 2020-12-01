rm -rf logs/*
rm -rf data.json

python3 master.py config.json R False &
python3 worker.py 4000 1 False &
python3 worker.py 4001 2 False &
python3 worker.py 4002 3 False &
python3 requests.py 20
echo
read -p "Press enter to continue(wait till all requests are completed)..."
pkill python
python3 analysis.py -c config.json -a R -b 2

rm -rf logs/*
sleep 1m

python3 master.py config.json RR False &
python3 worker.py 4000 1 False &
python3 worker.py 4001 2 False &
python3 worker.py 4002 3 False &
python3 requests.py 20
echo
read -p "Press enter to continue(wait till all requests are completed)..."
pkill python
python3 analysis.py -c config.json -a RR -b 2

rm -rf logs/*
sleep 1m

python3 master.py config.json LL False &
python3 worker.py 4000 1 False &
python3 worker.py 4001 2 False &
python3 worker.py 4002 3 False &
python3 requests.py 20
echo
read -p "Press enter to continue(wait till all requests are completed)..."
pkill python
python3 analysis.py -c config.json -a LL -b 2

python3 plot.py
