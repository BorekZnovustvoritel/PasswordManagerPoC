import src.persistence as u
import src.interface as app

p = app.PasswordManager("piesek")
p.add_service("smrad")
print(p.generate("smrad"))
