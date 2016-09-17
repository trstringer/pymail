SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/pymail.py"
CONFIGPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.pymail.sample.json"
echo "creating symlink to $SCRIPTPATH"
ln -s $SCRIPTPATH /usr/local/bin/pymail

echo "creating necessary folder structure"
mkdir -p ~/pymail/archive
mkdir -p ~/pymail/outbox/sent

cp $CONFIGPATH ~/.pymail
