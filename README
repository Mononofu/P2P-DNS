===============================================================================
===============================================================================
========    ______  ______   ______       _____    ______      _       ========
========   (_____ \(_____ \ (_____ \     (____ \  |  ___ \    | |      ========
========    _____) ) ____) ) _____) )___  _   \ \ | |   | |    \ \     ========
========   |  ____/ /_____/ |  ____/(___)| |   | || |   | |     \ \    ========
========   | |      _______ | |          | |__/ / | |   | | _____) )   ========
========   |_|     (_______)|_|          |_____/  |_|   |_|(______/    ========
========                                                               ========
===============================================================================
===============================================================================

                              ===== About =====

This is an alternative DNS system which relies on distribution to be censor
resistant. There is no central authority here! Records will be authenticated 
by a public/private key system, where only the owner of the private key can 
change the domain.

All nodes know all other nodes, and they also cache all known domains. This
makes it very difficult to tamper with records, since all existing nodes have
saved the public key of the domain owner and won't accept unsigned changes. An
attacker can only poison the cache of a new node, or try to flood the network
with "fake" domains.

Attack one will be prevented using a combination of democratic decisions (the
opinion of the majority is correct) and a web of trust (opinions of nodes are
weighted by your trust to them).

For attack two, similar tools as used in email spam prevention systems will be
deployed.

For more details, refer to http://www.furida.mu/blog/2010/12/11/p2p-dns/


                           ===== Installation =====

You need a SSL certificate for your node, just generate one:

openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes 

This is not a problem since we use ssl just for encryption, not authentication.
Note: The certificate needs to be named server.pem and reside in the same dir 
as the source code. If you don't like that, commit a patch.

You might also need the zmq module. If you are using Ubuntu, it's easy to 
install:

sudo add-apt-repository ppa:chris-lea/zeromq  
sudo aptitude update
sudo aptitude install python-zeromq


                              ===== Usage =====

To start the normal DNS server, type: 'twistd -y dns-server.py'
This server will try to connect to a p2p-dns server on the same machine, so if
you use two seperate machines adjust the constants at the begining of the file
accordingly.

To launch the actual p2p-dns server, use 'python p2p-dns.py' or './p2p-dns.py'
There are a few options in the config.py file, but it should work without
changes.

Don't use this on a production system! Right now you can register all domains, 
even those which already exist in the real dns system. Also, there are probably 
lots of security holes. You have been warned!


                              ===== Source =====

The official repo for this is https://github.com/Mononofu/P2P-DNS, so please 
look there if you want the newest version or want to commit a patch.



                             ===== License =====

This will use the GPLv3, except the normal DNS server (dns-server.py),  which 
was designed by Jochen Ritzel (http://stackoverflow.com/questions/4399512/python-dns-server-with-custom-backend/4401671#4401671)

