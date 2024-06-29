
for i in {2..2}
    do
        for j in {1..10}
            do
		echo "test $j"
		#mpiexec -n $i -tag-output -hostfile /nfs/hpc-unime-exam/hosts -display-map python /nfs/hpc-unime-exam/hpc-exam-opencl.py
        	#mpiexec -n $i -tag-output -hostfile /nfs/hpc-unime-exam/hosts -display-map python /nfs/hpc-unime-exam/hpc-exam-fullpython.py
		mpiexec -n $i -tag-output -hostfile /nfs/hpc-unime-exam/hosts -display-map python /nfs/hpc-unime-exam/hpc-exam-numpy.py
		mv /nfs/*stats.json /nfs/hpc-unime-exam/resultsdata/
            done
#	/nfs/hpc-unime-exam/clean.sh
done
