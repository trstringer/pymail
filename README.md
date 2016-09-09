# pymail

*Send and receive email from the command line.*

*Note: Gmail is the currently supported email provider*

## Setup

Run `install.sh` in the root repository directory

```
$ ./install.sh
```

## Configuration

**Location**: `~/.pymail`

```json
{
  "sender": {
    "auth": {
      "user": "user@gmail.com",
      "pass": "password"
    }
  },
  "addressBook": [
    { "name": "Person1", "email": "person1@email.com" },
    { "name": "Person2", "email": "person2@email.com" }
  ]
}
```

## Significant directories

 - **Inbox**: `~/pymail/`
 - **Inbox archive**: `~/pymail/archive/`
 - **Outbox**: `~/pymail/outbox/`
 - **Outbox sent**: `~/pymail/outbox/sent/`

## Usage

### List addressbook contents

```
$ pymail addressbook
```

### Send and receive email

```
$ pymail
```
