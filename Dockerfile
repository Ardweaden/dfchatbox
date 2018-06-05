FROM heroku/miniconda

# Grab requirements.txt.
ADD ./webapp/requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install -qr /tmp/requirements.txt