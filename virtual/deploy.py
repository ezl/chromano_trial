# Deployment procedure:
#  1) virtualenv .
#  2) source bin/activate
#  3) python deploy.py
import os


def deploy():
    """ Install required components """
    os.system('easy_install pip')
    os.system('pip install -r dev-requirements.txt')

# run deployment
if __name__ == "__main__":
    deploy()
