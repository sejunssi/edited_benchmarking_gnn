

# Command to download dataset:
#   bash script_download_molecules.sh


DIR=molecules/
cd $DIR


FILE=ZINC.pkl
if test -f "$FILE"; then
	echo -e "$FILE already downloaded."
else
	echo -e "\ndownloading $FILE..."
	curl https://www.dropbox.com/s/bhimk9p1xst6dvo/ZINC.pkl?dl=1 -o ZINC.pkl -J -L -k
fi




