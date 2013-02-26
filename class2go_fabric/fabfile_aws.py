__author__ = 'dglance'

from fabric.api import *
from fabric.colors import green as _green, yellow as _yellow
from cuisine import *
import boto
import boto.ec2
from django.template import loader, Context
import time
from django.conf import settings
from class2go_fabric import *

env.user = settings.ADMIN_USER

def create_server():
    """
    Creates EC2 Instance
    """
    print(_green("Started..."))
    print(_yellow("...Creating EC2 instance..."))

    conn = boto.ec2.connect_to_region(settings.EC2_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


    image = conn.get_image(settings.EC2_AMI)

    reservation = image.run(1, 1, key_name=settings.EC2_KEY_PAIR, security_groups={settings.EC2_SECURITY},
                            instance_type=settings.EC2_INSTANCE_TYPE)

    instance = reservation.instances[0]
    conn.create_tags([instance.id], {"Name":settings.EC2_TAG})
    while instance.state == u'pending':
        print(_yellow("Instance state: %s" % instance.state))
        time.sleep(10)
        instance.update()

    print(_green("Instance state: %s" % instance.state))
    print(_green("Public dns: %s" % instance.public_dns_name))

    return instance.public_dns_name
