SAMPLE=$1
MFILE=`ls ../data/movement_data/ | grep export | grep $SAMPLE`
echo $SAMPLE

python3 get_time_splices.py ../data/movement_data/$MFILE  ../data/gameplay_data/$SAMPLE --tsfile ../data/valid_time_stamps/$SAMPLE"_valid_time_stamps.pickle"
