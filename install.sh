SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/pymail.py"
echo "creating symlink to $SCRIPTPATH"
ln -s $SCRIPTPATH /usr/local/bin/pymail

echo "creating necessary folder structure"
mkdir -p ~/pymail/archive
mkdir -p ~/pymail/outbox/sent
