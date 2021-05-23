#####################################################################################
# First we define the general parameters of the run                                 #
#####################################################################################
SUBMISSION='visualization'
DEBUG=0 # 0 = Not a debug run, 1 = a debug run
#0=first order, 1=coastal, 2=stochastic beaching/resuspension, 3=coast type dependent, 4 = Turrell (2020)
#5 = Cozar based fragmentation, 6 = Size dependent transport
SCENARIO=6
#Which input distribution do we want to use? 0=Jambeck, 1=lebreton, 2=point release, 3=uniform release
INPUT=1
#Inclusion of Stokes drift. 0 = include stokes, 1 = do not include stokes
STOKES=0
#Ubelix server, so server==1
SERVER=1


export SUBMISSION
export SCENARIO
export STOKES
export SERVER
export INPUT

#Now, we can set the job name prefix
if [ "$SCENARIO" -eq "0" ]; then
	RUNNAMEPREFIX="Visualization_AdvDifOnly"
elif [ "$SCENARIO" -eq "1" ]; then
	RUNNAMEPREFIX="Visualization_Prox"
elif [ "$SCENARIO" -eq "2" ]; then
	RUNNAMEPREFIX="Visualization_Stochastic"
elif [ "$SCENARIO" -eq "3" ]; then
        RUNNAMEPREFIX="Visualization_SDResus"
elif [ "$SCENARIO" -eq "4" ]; then
        RUNNAMEPREFIX="Visualization_Turrell"
elif [ "$SCENARIO" -eq "5" ]; then
        RUNNAMEPREFIX="Visualization_KaandorpFrag"
elif [ "$SCENARIO" -eq "6" ]; then
        RUNNAMEPREFIX="Visualization_SizeTransport"
fi

#####################################################################################
# Now the part where we create the submission file                                  #
#####################################################################################
runname=$RUNNAMEPREFIX
part1="#!/bin/sh"
part2="#SBATCH --mail-type=begin,end,fail"
part3="#SBATCH --mail-user=victor.onink@climate.unibe.ch"
part4="#SBATCH --job-name="$runname
part5="#SBATCH --output="runOutput/$runname".o%j"
part6="#SBATCH --mem-per-cpu=20G"
if [ "$DEBUG" -eq "0" ]; then
#      part7="#SBATCH --time=95:59:00"
      part7="#SBATCH --time=20:00:00"
      part8="#SBATCH --partition=epyc2"
      part9='#SBATCH --qos=job_epyc2'
else
      part7="#SBATCH --time=00:19:00"
      part8="#SBATCH --partition=epyc2"
      part9='#SBATCH --qos=job_epyc2_debug'
fi
#loading the bash and setting the environment
part10="source /storage/homefs/vo18e689/.bash_profile"
part11="source /storage/homefs/vo18e689/anaconda3/bin/activate py3_parcels"
part12='cd "/storage/homefs/vo18e689/codes/Next-Stage-Plastic-Beaching/"'
#And now the actual running of the code
part13="python src/main.py -p 10 -v"
#and now the creation of the submission file
for i in {1..13}
do
partGrab="part"$i
echo ${!partGrab} >> jobsubmissionFile_${run}_${restartnum}.sh
done

sbatch jobsubmissionFile_${run}_${restartnum}.sh

rm jobsubmissionFile_${run}_${restartnum}.sh
