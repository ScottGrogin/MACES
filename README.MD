# M.A.C.E.S (Malik's Automated Credit Entry System)

This is the source code for the automated credit entry system I made for my LARP group.

This project uses python 3.12.3

To set up locally first, follow the docker instructions to set up ORK3

https://github.com/amtgard/ORK3/tree/master

After ORK3 is set up, create a new virtual env

`pyenv install 3.12.3`

`pyenv virtualenv 3.12.3 maces`

`pyenv activate maces`

Then install requirements

`python -m pip install -r requirements.txt`

Finally run the flask app

`python app.py`
