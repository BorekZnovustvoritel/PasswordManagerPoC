import src.app as app
import src.utils as utils
import src.config as config

manager = app.PasswordManager(user_password="piesek")
manager.add_service(
    name="seznam",
    length=32,
    iterations=1000,
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*+-_",
)
print(manager.generate("seznam"))
print(utils.hash_db())
print(manager.get_service("seznam"))

manager.add_service(name="1", length=10, iterations=1, alphabet="1234567890")
print(manager.generate("1"))
