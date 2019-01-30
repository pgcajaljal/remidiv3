import os
import subprocess


try:
	# cmd = ["darknet", "detector", "test", "plasmodium-obj.data", "plasmodium-tiny.cfg", "final.weights",
	# "-thresh 0.25"]
	cmd = ['plasmodiumfiles\\darknet-plasmodium.bat']
	p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE, shell = True)
	out,err = p.communicate()
	return out,err
except: 
	return err
