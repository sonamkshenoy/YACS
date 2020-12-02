cd ~/Desktop/hadoop/hadoop-3.2.1/YACS/

rm -rf logs/*
rm -rf Analysis/data.json

python3 master.py config.json R False &
python3 worker.py 4000 1 False &
python3 worker.py 4001 2 False &
python3 worker.py 4002 3 False &
python3 requests.py 20
echo
read -p "Press enter to continue(wait till all requests are completed)..."
pkill python
python3 Analysis/analysis.py --config config.json --algo R --bin_interval 2 --data_file Analysis/data.json

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
python3 Analysis/analysis.py --config config.json --algo RR --bin_interval 2 --data_file Analysis/data.json

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
python3 Analysis/analysis.py --config config.json --algo LL --bin_interval 2 --data_file Analysis/data.json

python3 Analysis/plot.py --data_file Analysis/data.json
