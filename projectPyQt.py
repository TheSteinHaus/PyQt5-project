import sys
from threading import Timer
from mycalc import *
from PyQt5.QtWidgets import *

from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QRadioButton, QLabel
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QTime, QDate, QDateTime, QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView, QWebEnginePage as QWebPage, QWebEngineSettings as QWebSettings
import sqlite3
import re
import time
import json
from pyowm import OWM

with open('apps.json', encoding='utf-8') as file:
    apps = json.load(file)

with open('products.json', encoding='utf-8') as file:
    products = json.load(file)


class Login(QDialog):

    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.welcome = Welcome()

        self.LoginButton.clicked.connect(self.loginFunction)
        self.Pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.goToCreate)
        self.invalidLabel_3.setVisible(False)
        self.invalidLabel_4.setVisible(False)

    def loginFunction(self):
        email = self.Email.text()
        password = self.Pass.text()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT email,password FROM user_info")
        val = cursor.fetchall()
        for x in val:
            if ((email == x[0] and email !='') and (password == x[1] and password != '')):
                print("welcome")
                self.goWelcome()
                break
            elif email != x[0]:
                self.invalidLabel_3.setVisible(True)
                self.invalidLabel_4.setVisible(True)
            elif email != x[0] and password == x[1]:
                self.invalidLabel_3.setVisible(False)
                self.invalidLabel_4.setVisible(True)
            elif email == x[0] and password != x[1]:
                self.invalidLabel_3.setVisible(True)
                self.invalidLabel_4.setVisible(False)
        else:
            print('No user Found')

    def goWelcome(self):
        self.welcome.show()

    def goToCreate(self):
        creatacc = createAccount()
        widget.addWidget(creatacc)
        widget.setCurrentIndex(widget.currentIndex()+1)


class createAccount(QDialog):
    gender = 'Male'

    def __init__(self):
        super(createAccount, self).__init__()
        loadUi("creatAccount.ui", self)
        widget.setFixedWidth(480)
        widget.setFixedHeight(620)
        self.invalidLabel_2.setVisible(False)
        self.invalidLabel.setVisible(False)
        self.creatAcc.clicked.connect(self.creatAccFun)
        self.Pass_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.Pass_3.setEchoMode(QtWidgets.QLineEdit.Password)
        self.backtologin.clicked.connect(self.goToBack)
        self.invalidLabel.clicked.connect(self.popMessage)
        self.invalidLabel_2.clicked.connect(self.popMessage)
        self.creatAcc.clicked.connect(self.creatAccFun)
        self.invalidfirstname.setVisible(False)
        self.invalidfamilyname.setVisible(False)

    def creatAccFun(self):
        gender = 'Male'
        if self.Female.isChecked():
            gender = 'Female'
        firstname = (self.firstName.text()).lower()
        surname = (self.familyName.text()).lower()
        if 3 < len(firstname) < 12:
            self.invalidfirstname.setVisible(True)
        if len(surname) < 3:
            self.invalidfamilyname.setVisible(True)
        email = (self.Email.text()).lower()
        if self.passCheck():
            Pass = self.Pass_2.text()
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS user_info(email TEXT, firstname TEXT, surname TEXT, password TEXT, gender TEXT)")
            c.execute("INSERT INTO user_info(email, firstname, surname, password, gender) VALUES (?, ?, ?, ?, ?)", (email, firstname, surname, Pass, gender))
            conn.commit()
            c.close()
            conn.close()
            self.goToBack()
        else:
            self.invalidLabel.setVisible(True)
            self.invalidLabel_2.setVisible(True)

    def passCheck(self):
        password = self.Pass_2.text()
        if re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'[0-9]', password) and (self.Pass_2.text()==self.Pass_3.text()) and ((4<len(self.Pass_2.text())<12) and (4<len(self.Pass_3.text())<12)):
            return True
        else:
            print("\npassword must be > 6 and contain A-Z,a-z,0-9 ... ", self.Pass_2.text(),self.Pass_3.text(),len(self.Pass_2.text()))
            return False

    def goToBack(self):
        creatacc = Login()
        widget.addWidget(creatacc)
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def popMessage(self):
        msg = Message()
        widget.addWidget(msg)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Message(QDialog):

    def __init__(self):
        super(Message, self).__init__()
        loadUi("message.ui", self)
        widget.setFixedWidth(480)
        widget.setFixedHeight(620)
        self.backtocreat.clicked.connect(self.gotoback2)

    def gotoback2(self):
        g = createAccount()
        widget.addWidget(g)
        widget.setCurrentIndex(widget.currentIndex() - 1)
        print(widget.currentIndex())


class Welcome(QDialog):
    def __init__(self):
        super(Welcome, self).__init__()
        self.cal = MyCalc()
        self.ch = Shop()
        loadUi("welcome.ui", self)
        self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
        self.setFixedWidth(1365)
        self.setFixedHeight(921)
        self.pushButton.clicked.connect(self.getWeather)

        for item in apps:

            pixmap = QPixmap(item['src'])
            item = QListWidgetItem(QIcon(pixmap), item['name'])

            self.listWidget.addItem(item)

        self.listWidget.itemActivated.connect(self.launch)

        self.webbrowser = QWebView(self)
        self.gridLayout_2.addWidget(self.webbrowser)
        self.webbrowser.load(QUrl('https://meduza.io/'))

        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)

    def launch(self, item):
        if item.text() == 'Калькулятор':
            self.cal.show()
        elif item.text() == 'Чек из KFC':
            self.ch.show()

    def showTime(self):

        current_time = QDateTime.currentDateTime()
        label_time = current_time.toString(Qt.DefaultLocaleLongDate)
        self.label_2.setText(label_time)

    def getWeather(self):
        owm = OWM('6d00d1d4e704068d70191bad2673e0cc')
        city = self.lineEdit.text()

        obs = owm.weather_manager().weather_at_place(city)
        w = obs.weather

        t = w.temperature("celsius")
        t1 = t['temp']
        t2 = t['feels_like']
        t3 = t['temp_max']
        t4 = t['temp_min']
        wi = w.wind()['speed']
        humi = w.humidity
        cl = w.clouds
        st = w.status
        dt = w.detailed_status
        ti = w.reference_time('iso')
        pr = w.pressure['press']
        vd = w.visibility_distance

        answer = "В городе " + str(city) + " температура " + str(t1) + " °C" + "\n" + \
              "Максимальная температура " + str(t3) + " °C" +"\n" + \
              "Минимальная температура " + str(t4) + " °C" + "\n" + \
              "Ощущается как " + str(t2) + " °C" + "\n" + \
              "Скорость ветра " + str(wi) + " м/с" + "\n" + \
              "Давление " + str(pr) + " мм.рт.ст" + "\n" + \
              "Влажность " + str(humi) + " %" + "\n" + \
              "Видимость " + str(vd) + " метров" + "\n" + \
              "Описание " + str(st)

        self.textEdit.setText(answer)


class MyCalc(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.initUI()

    def initUI(self):
        self.nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

        self.ui.pushButton_n0.clicked.connect(lambda: self.ui.NumLine.insert('0'))
        self.ui.pushButton_n1.clicked.connect(lambda: self.ui.NumLine.insert('1'))
        self.ui.pushButton_n2.clicked.connect(lambda: self.ui.NumLine.insert('2'))
        self.ui.pushButton_n3.clicked.connect(lambda: self.ui.NumLine.insert('3'))
        self.ui.pushButton_n4.clicked.connect(lambda: self.ui.NumLine.insert('4'))
        self.ui.pushButton_n5.clicked.connect(lambda: self.ui.NumLine.insert('5'))
        self.ui.pushButton_n6.clicked.connect(lambda: self.ui.NumLine.insert('6'))
        self.ui.pushButton_n7.clicked.connect(lambda: self.ui.NumLine.insert('7'))
        self.ui.pushButton_n8.clicked.connect(lambda: self.ui.NumLine.insert('8'))
        self.ui.pushButton_n9.clicked.connect(lambda: self.ui.NumLine.insert('9'))
        self.ui.pushButton_m.clicked.connect(lambda: self.ui.NumLine.insert('('))
        self.ui.pushButton_point.clicked.connect(lambda: self.ui.NumLine.insert(')'))
        self.ui.pushButton_pc.clicked.connect(self.point)
        self.ui.pushButton_add.clicked.connect(self.plus)
        self.ui.pushButton_sub.clicked.connect(self.minus)
        self.ui.pushButton_mul.clicked.connect(self.mult)
        self.ui.pushButton_div.clicked.connect(self.div)
        self.ui.pushButton_ac.clicked.connect(self.ui.NumLine.clear)
        self.ui.pushButton_eq.clicked.connect(self.equals)

    def equals(self):
        try:
            if self.ui.NumLine.text()[0] != '0' and (self.ui.NumLine.text()[-1] in self.nums or self.ui.NumLine.text()[-1] == ')'):
                try:
                    f = self.ui.NumLine.text()
                    g = eval(f)
                    self.ui.NumLine.setText(str(g))

                except ZeroDivisionError:
                    QMessageBox.critical(self, "Ошибка", "Деление на 0 строго запрещено")
        except IndexError:
            QMessageBox.critical(self, "Ошибка", "Введите число")
        except TypeError:
            QMessageBox.critical(self, "Ошибка", "Что-то пошло не так")


    def plus(self):
        if self.ui.NumLine.text()[-1] in self.nums:
            self.ui.NumLine.insert('+')

    def minus(self):
        if self.ui.NumLine.text()[-1] in self.nums:
            self.ui.NumLine.insert('-')

    def mult(self):
        if self.ui.NumLine.text()[-1] in self.nums:
            self.ui.NumLine.insert('*')

    def div(self):
        if self.ui.NumLine.text()[-1] in self.nums:
            self.ui.NumLine.insert('/')

    def point(self):
        try:
            if self.ui.NumLine.text()[-1] == '.':
                pass
            else:
                self.ui.NumLine.insert('.')
        except IndexError:
            QMessageBox.critical(self, "Ошибка", "Введите число")


class UiMainWindow(object):
    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 290)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(10, 20, 580, 210))
        self.listWidget.setObjectName("listWidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(390, 250, 200, 30))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslate_ui(self, MainWindow):
        MainWindow.setWindowTitle("Терминал")
        self.pushButton.setText("Купить")


class UiSetValue(object):
    def setup_ui(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(210, 80)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 40, 130, 35))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.spinBox = QtWidgets.QSpinBox(Dialog)
        self.spinBox.setGeometry(QtCore.QRect(10, 10, 190, 30))
        self.spinBox.setObjectName("spinBox")

        self.retranslate_ui(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslate_ui(self, Dialog):
        Dialog.setWindowTitle("Выберите количество")


class UiCheque(object):
    def setup_ui(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 300)
        self.centralwidget = QtWidgets.QWidget(Form)
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 50, 580, 230))
        self.textBrowser.setObjectName("textBrowser")

    def retranslate_ui(self, Form):
        Form.setWindowTitle("Чек")


value = 0


class Shop(QMainWindow, UiMainWindow):
    def __init__(self):

        super().__init__()
        self.cheque = Cheque()
        self.setup_ui(self)
        self.listWidget.setViewMode(QListWidget.IconMode)

        for item in products:

            pixmap = QPixmap(item['src'])
            item = QListWidgetItem(QIcon(pixmap), item['name'] + ' - ' + item['cost'])
            item.setCheckState(QtCore.Qt.Unchecked)

            self.listWidget.addItem(item)

        self.listWidget.itemChanged.connect(self.changed)
        self.prod = dict()
        self.prices = dict()
        self.pushButton.clicked.connect(self.get_cheque)

    def changed(self, item):

        pos, price = item.text().split(' - ')
        self.prices[pos] = int(price)

        if item.checkState():

            window = SetValue()
            window.show()
            window.exec()
            self.prod[pos] = value

        else:

            self.prod[item.text()] = 0

    def get_cheque(self):

        total_price = 0
        final_text = str()

        for name in self.prod.keys():

            if self.prod[name] > 0:

                current_price = self.prices[name] * self.prod[name]

                if 1 == current_price % 10:

                    rubles = 'рубль'

                elif 2 <= current_price % 10 <= 4:

                    rubles = 'рубля'

                else:

                    rubles = 'рублей'

                final_text += '"{}" в количестве {} шт., \t {} {}.\n'.format(name, self.prod[name], current_price, rubles)
                total_price += current_price

        if 1 == total_price % 10:

            rubles = 'рубль'

        elif 2 <= total_price % 10 <= 4:

            rubles = 'рубля'

        else:

            rubles = 'рублей'

        final_text += "Сумма к оплате: {} {}".format(total_price, rubles)
        self.cheque.textBrowser.setText(final_text)
        self.cheque.show()


class Cheque(QWidget, UiCheque):
    def __init__(self):
        super().__init__()
        self.setup_ui(self)


class SetValue(QDialog, UiSetValue):
    def __init__(self):
        super().__init__()
        self.setup_ui(self)
        self.buttonBox.accepted.connect(self.get_value)

    def get_value(self):
        global value
        value = self.spinBox.value()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainWin = Login()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainWin)
    widget.setFixedWidth(480)
    widget.setFixedHeight(620)
    widget.show()
    app.exec()
