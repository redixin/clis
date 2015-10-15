How to boot cloud image on localhost
####################################

Short answer
************

Use cloud-init-server::

    sudo apt-get install python3-pip
    sudo pip3 install cloud-init-server
    sudo iptables -t nat -I PREROUTING -d 169.254.169.254/32 -p tcp -m tcp --dport 80 -j REDIRECT --to-ports 8081
    cloud-init-server

Now you can boot images downloaded from `here <https://cloud-images.ubuntu.com/>`_
(filename matches `*-disk1.img`).

Known to work vivid and trusty.

Server will feed your ssh key (~/.ssh/id_rsa.pub) to image and
you can log in via ssh. Default username for ubuntu images is `ubuntu`.

After boot you may want to uninstall cloud-init from VM and turn it to usual, non-cloud image. So go ahead.

Long answer
***********

`Here should be more info about cloud-init`
