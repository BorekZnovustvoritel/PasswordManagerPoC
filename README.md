# PasswordManagerPoC

Free time project to try and make my own Password Manager using highly secure algorithms. Work in progress. Also for now it's just a Proof of Concept (PoC).

## Before running

- Make sure you have Python and Qt5 installed.

## How to run

### First run

- `git clone https://github.com/BorekZnovustvoritel/PasswordManagerPoC.git`
- `cd PasswordManagerPoC`
- `python -m venv venv` (`python` can use different keyword depending on your operating system.
Try `py` (Windows) or `python3` (Debian))
- `source venv/bin/activate` (on Windows `source venv/Scripts/activate`)
- `pip install -r dependencies.txt`
- `python ./main.py`

### Next runs

- `source venv/bin/activate`
- `python ./main.py`

## How to actually use this

When opened for the first time, you will be prompted to enter a password. **Make sure this password is strong, not used anywhere else and make sure to remember it. There is no way to reset the main password (yet).** On every other login after this, you will need to enter the exact same password or you will not be able to access your own data because of strong encryption (AES_256_CBC).

Add your services via the `Add` button on the main window, choose the password parameters and press `Ok`. The selected password will be copied to your clipboard upon a doubleclick.

Delete a service with a right click or sigleclick followed by pressing the `del` key on your keyboard.

This project is a work in progress and by using this, I take no liability over any lost data.

Protect and backup your `.db` file. If this file corrupts, all the saved passwords will be lost. The database files may incompatible between versions.

## Credits

This repository uses [PyCryptoDome](https://www.pycryptodome.org/en/latest/) and [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) modules available via Python Pip.

