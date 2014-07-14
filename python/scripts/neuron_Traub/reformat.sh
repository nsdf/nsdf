mkdir ./i/tmp;
cd i;
#IMPORTANT, this assumes, the files are in ascending order of time.
#pushes the 5th column element into a file named by the second column element
parallel -j 7 awk -F '\t' '{print $5 >> "./tmp/"$2".dat";}' -- *.dat;
cd ..;
mkdir ./v/tmp;
cd v;
parallel -j 7 awk -F '\t' '{print $5 >> "./tmp/"$2".dat";}' -- *.dat;
cd ..;
