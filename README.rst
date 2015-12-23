How to use cloud images without cloud
#####################################

Use clis::

    sudo apt-get install python3-pip
    sudo pip3 install clis
    sudo iptables -t nat -I PREROUTING -d 169.254.169.254/32 -p tcp -m tcp --dport 80 -j REDIRECT --to-ports 8088
    clis

Now you can boot images downloaded from
`here <https://cloud-images.ubuntu.com/>`_ (filename matches `*-disk1.img`).

Known to work with vivid and trusty.

Server will feed your ssh key (~/.ssh/id_rsa.pub) to image and you can log in
via ssh. Default username for ubuntu images is `ubuntu`.

It is poosible to specify alternate ssh public key(s) by command line::

    clis -k ~/.ssh/alternate.pub -k ~/.ssh/backup.pub

When clis is running you may boot cloud image and see ip address of VM in
logs. Just ssh to this address::

    ssh ubuntu@192.168.122.42

You may want to uninstall cloud-init from VM and turn it to non-cloud image::

    ubuntu@vm-192-168.122.42:~$ sudo apt-get remove cloud-init

What is cloud-init
******************

Cloud image is usual image with `cloud-init` package installed. Cloud-init is
software which trying to access magic url http://169.254.169.254/ and get
VM configuration from there. Different versions of cloud-init "protocol"
supported by different versions of images. All this versions are poorly
documented or not documented at all.
