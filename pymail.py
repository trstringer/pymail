#!/usr/bin/env python3
from datetime import datetime
from email import parser
import json
import os
import poplib
import re
import smtplib
import sys

"""
Email class to handle the data and operations of emails
"""
class Email:
    def __init__(self, sender, to, subject, body, email_filename=None):
        self.sender = sender
        self.to = to
        self.subject = subject
        self.body = body
        self.email_filename = email_filename

    def __str__(self):
        return '{}\n{}\n{}'.format(self.sender, self.subject, self.body)

    def recipient_is_email_address(self):
        return re.search(r'.*@.*\..*', self.to) is not None

    def send(self):
        config = Config()
        if not self.recipient_is_email_address():
            found_address = False
            for address in config.addressbook:
                if self.to.lower() == address.name.lower():
                    self.to = address.address
                    found_address = True
            if not found_address:
                raise ValueError('unable to resolve "{}" in addressbook'.format(self.to))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(config.username, config.password)
        message = 'Subject: %s\n\n%s' % (self.subject, self.body)
        server.sendmail(config.username, self.to, message)
        server.close()

    def archive(self):
        config = Config()
        if self.sender == config.username:
            # in this case this is an outgoing email
            FileSystem.archive_sent_email(self)
        elif self.to == config.username:
            FileSystem.archive_inbox_email(self)
        else:
            raise ValueError('unable to determine if sent or received email')

    def save_in_inbox(self):
        FileSystem.cache_email_in_inbox(self)

    def generate_filename(self):
        return '{}_{}.email'.format(
            datetime.now().strftime(r'%Y%m%d%H%M%S%f'), 
            self.sender.replace(' ', '').replace('<', '_').replace('>', '_'))

    @staticmethod
    def receive():
        config = Config()
        connection = poplib.POP3_SSL('pop.gmail.com')
        connection.user(config.username)
        connection.pass_(config.password)
        messages = [connection.retr(i) for i in range(1, len(connection.list()[1]) + 1)]
        messages = [b"\n".join(temp_message[1]).decode('utf-8') for temp_message in messages]
        messages = [parser.Parser().parsestr(temp_message) for temp_message in messages]
        for message in messages:
            yield Email(message['from'], message['to'], message['subject'], message._payload)
        connection.quit()

    @staticmethod
    def parse(sender, raw_email):
        temp_raw_email = raw_email.splitlines()
        recipient = temp_raw_email.pop(0)
        subject = temp_raw_email.pop(0)
        body = '\n'.join(temp_raw_email)
        return Email(sender, recipient, subject, body)

"""
Address class to store a single address
"""
class Address:
    def __init__(self, name, address):
        self.name = name
        self.address = address

    def __str__(self):
        return '{} :: {}'.format(self.name, self.address)
"""
Config class to provide easy-to-consume configuration options
"""
class Config:
    def __init__(self):
        self.file_system = FileSystem()
        self.addressbook = []
        self.__parse(self.file_system.CONFIG_FILENAME)

    def __parse(self, config_filename):
        with open(config_filename, 'r') as config_file:
            data = json.load(config_file)
        self.username = data['sender']['auth']['user']
        self.password = data['sender']['auth']['pass']
        for address in data['addressBook']:
            self.addressbook.append(Address(address['name'], address['email']))

"""
FileSystem object to provide file system operations like 
caching and retrieving email files
"""
class FileSystem:
    CONFIG_FILENAME = os.path.join(os.path.expanduser('~'), '.pymail')
    INBOX_DIRECTORY = os.path.join(os.path.expanduser('~'), 'pymail')
    INBOX_ARCHIVE_DIRECTORY = os.path.join(os.path.expanduser('~'), 'pymail', 'archive')
    OUTBOX_DIRECTORY = os.path.join(os.path.expanduser('~'), 'pymail', 'outbox')
    SENT_DIRECTORY = os.path.join(os.path.expanduser('~'), 'pymail', 'outbox', 'sent')

    @staticmethod
    def __outbox_filenames():
        for email_file in os.listdir(FileSystem.OUTBOX_DIRECTORY):
            if (os.path.isfile(os.path.join(FileSystem.OUTBOX_DIRECTORY, email_file)) and
                    re.search(r'.*\.email$', email_file) is not None):
                yield os.path.join(FileSystem.OUTBOX_DIRECTORY, email_file)

    @staticmethod
    def outbox_emails():
        config = Config()
        for email_file in FileSystem.__outbox_filenames():
            with open(email_file, 'r') as ef:
                email = Email.parse(config.username, ef.read())
                email.email_filename = email_file
                yield email

    @staticmethod
    def archive_inbox_email(email):
        if not email.email_filename:
            raise ValueError('no filename included in Email object')
        else:
            filename_without_path = os.path.basename(email.email_filename)
            new_filename = os.path.join(FileSystem.INBOX_ARCHIVE_DIRECTORY, filename_without_path)
            os.rename(email.email_filename, new_filename)

    @staticmethod
    def archive_sent_email(email):
        if not email.email_filename:
            raise ValueError('no filename included in Email object')
        else:
            filename_without_path = os.path.basename(email.email_filename)
            filename_without_path = '{}_{}'.format(datetime.now().strftime(r'%Y%m%d%H%M%S%f'), filename_without_path)
            new_filename = os.path.join(FileSystem.SENT_DIRECTORY, filename_without_path)
            os.rename(email.email_filename, new_filename)

    @staticmethod
    def cache_email_in_inbox(email):
        with open(os.path.join(FileSystem.INBOX_DIRECTORY, email.generate_filename()), 'w') as email_file:
            email_file.write(str(email))

"""
main code execution
"""
def main(argv):
    config = Config()

    if len(argv) > 1 and argv[1].lower() == 'addressbook':
        for address in config.addressbook:
            print(str(address))
    else:
        # send all emails that are pending
        counter = 0
        try:
            for email in FileSystem.outbox_emails():
                email.send()
                counter += 1
                email.archive()
        except Exception as e:
            print(e)

        print('sent {} email(s)'.format(counter))

        #receive new emails
        counter = 0
        try:
            for email in Email.receive():
                email.save_in_inbox()
                counter += 1
        except Exception as e:
            print(e)

        print('received {} email(s)'.format(counter))

main(sys.argv)
