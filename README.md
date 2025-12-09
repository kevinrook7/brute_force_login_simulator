# brute_force_login_simulator
Brute Force Login Simulator to recognize effect of rate limiting and account lockout

The main goal of this project was to understand how a brute force method of hacking works and to test out two methods of defences—rate limiting and account lockout.

To achieve this an attacker and server was created. The server.py consisted of an API login endpoint  created using flask and allowed me to enable rate limiting and/or account lockout. I could also adjust the rate for rate limiting and also the time for account lockout. The attacker.py on the other hand sends login attempts to the endpoint from a list of passwords from the passwords.txt file. It also tracked staistics like total attempts, succesful attempts, lockouts and rate limiting triggers.
