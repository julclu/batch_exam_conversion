#!/usr/bin/csh 
if ($#argv > 1 ) then
    echo "Please enter the path to the .csv file containing the list of"
    echo "bnum/tnum that you'd like to ensure are processed correctly."
    exit(1)
endif
set n = $1 
set b = `more $n | cut -d"," -f1`
set t = `more $n | cut -d"," -f2`

@ i = 1

@ m = `echo $n | cut -d"." -f2`

set recgli_path_root = "/data/RECglioma/"

echo "number of scans set"

while ($i <= $m)
	## set bnum/tnum 
	set bnum = `echo ${b} | cut -d" " -f$i`
	set tnum = `echo ${t} | cut -d" " -f$i`
	
	## keep track of which bnum/tnum we're on
	echo $i $bnum $tnum

	## go to correct directory 
	cd $recgli_path_root
	pwd
	cd $bnum
	pwd
	cd $tnum
	pwd
	if(-d 'svk_roi_analysis') then
		cd 'svk_roi_analysis'
		pwd
		ls | grep -v $tnum | xargs rm
	endif 
	@ i = $i + 1

end