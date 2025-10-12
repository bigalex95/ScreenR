# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'screen_recorder_v1.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QTabWidget,
    QVBoxLayout, QWidget)
import resources.resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QSize(600, 400))
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(15, 15, 15, 15)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.recorderTab = QWidget()
        self.recorderTab.setObjectName(u"recorderTab")
        self.verticalLayout_7 = QVBoxLayout(self.recorderTab)
        self.verticalLayout_7.setSpacing(10)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(-1, 10, -1, 10)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(10)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.recordButton = QPushButton(self.recorderTab)
        self.recordButton.setObjectName(u"recordButton")
        icon = QIcon()
        icon.addFile(u":/icons/start.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.recordButton.setIcon(icon)
        self.recordButton.setIconSize(QSize(64, 64))

        self.verticalLayout_3.addWidget(self.recordButton)

        self.pauseButton = QPushButton(self.recorderTab)
        self.pauseButton.setObjectName(u"pauseButton")
        icon1 = QIcon()
        icon1.addFile(u":/icons/pause.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pauseButton.setIcon(icon1)
        self.pauseButton.setIconSize(QSize(32, 32))

        self.verticalLayout_3.addWidget(self.pauseButton)


        self.verticalLayout_7.addLayout(self.verticalLayout_3)

        self.previewLabel = QLabel(self.recorderTab)
        self.previewLabel.setObjectName(u"previewLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.previewLabel.sizePolicy().hasHeightForWidth())
        self.previewLabel.setSizePolicy(sizePolicy)
        self.previewLabel.setMinimumSize(QSize(320, 180))
        self.previewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_7.addWidget(self.previewLabel)

        self.tabWidget.addTab(self.recorderTab, "")
        self.settingsTab = QWidget()
        self.settingsTab.setObjectName(u"settingsTab")
        self.verticalLayout_6 = QVBoxLayout(self.settingsTab)
        self.verticalLayout_6.setSpacing(15)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.settingsTab)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.systemAudioButton = QPushButton(self.settingsTab)
        self.systemAudioButton.setObjectName(u"systemAudioButton")

        self.horizontalLayout.addWidget(self.systemAudioButton)

        self.microphoneButton = QPushButton(self.settingsTab)
        self.microphoneButton.setObjectName(u"microphoneButton")

        self.horizontalLayout.addWidget(self.microphoneButton)

        self.noneAudioButton = QPushButton(self.settingsTab)
        self.noneAudioButton.setObjectName(u"noneAudioButton")

        self.horizontalLayout.addWidget(self.noneAudioButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_6.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_2 = QLabel(self.settingsTab)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.fullScreenButton = QPushButton(self.settingsTab)
        self.fullScreenButton.setObjectName(u"fullScreenButton")

        self.horizontalLayout_2.addWidget(self.fullScreenButton)

        self.selectAreaButton = QPushButton(self.settingsTab)
        self.selectAreaButton.setObjectName(u"selectAreaButton")

        self.horizontalLayout_2.addWidget(self.selectAreaButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout_6.addLayout(self.verticalLayout_2)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_3 = QLabel(self.settingsTab)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lowQualityButton = QPushButton(self.settingsTab)
        self.lowQualityButton.setObjectName(u"lowQualityButton")

        self.horizontalLayout_3.addWidget(self.lowQualityButton)

        self.mediumQualityButton = QPushButton(self.settingsTab)
        self.mediumQualityButton.setObjectName(u"mediumQualityButton")

        self.horizontalLayout_3.addWidget(self.mediumQualityButton)

        self.highQualityButton = QPushButton(self.settingsTab)
        self.highQualityButton.setObjectName(u"highQualityButton")

        self.horizontalLayout_3.addWidget(self.highQualityButton)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout_6.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_4 = QLabel(self.settingsTab)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_5.addWidget(self.label_4)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.threeSecondsButton = QPushButton(self.settingsTab)
        self.threeSecondsButton.setObjectName(u"threeSecondsButton")

        self.horizontalLayout_4.addWidget(self.threeSecondsButton)

        self.fiveSecondsButton = QPushButton(self.settingsTab)
        self.fiveSecondsButton.setObjectName(u"fiveSecondsButton")

        self.horizontalLayout_4.addWidget(self.fiveSecondsButton)

        self.tenSecondsButton = QPushButton(self.settingsTab)
        self.tenSecondsButton.setObjectName(u"tenSecondsButton")

        self.horizontalLayout_4.addWidget(self.tenSecondsButton)

        self.noneTimerButton = QPushButton(self.settingsTab)
        self.noneTimerButton.setObjectName(u"noneTimerButton")

        self.horizontalLayout_4.addWidget(self.noneTimerButton)


        self.verticalLayout_5.addLayout(self.horizontalLayout_4)


        self.verticalLayout_6.addLayout(self.verticalLayout_5)

        self.tabWidget.addTab(self.settingsTab, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.recordButton.setText(QCoreApplication.translate("MainWindow", u"Start Recording", None))
        self.pauseButton.setText(QCoreApplication.translate("MainWindow", u"Pause", None))
        self.previewLabel.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.recorderTab), QCoreApplication.translate("MainWindow", u"Recorder", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Audio Input", None))
        self.systemAudioButton.setText(QCoreApplication.translate("MainWindow", u"System Audio", None))
        self.microphoneButton.setText(QCoreApplication.translate("MainWindow", u"Microphone", None))
        self.noneAudioButton.setText(QCoreApplication.translate("MainWindow", u"None", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Recording Area", None))
        self.fullScreenButton.setText(QCoreApplication.translate("MainWindow", u"Full Screen", None))
        self.selectAreaButton.setText(QCoreApplication.translate("MainWindow", u"Select Area", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Recording Quality", None))
        self.lowQualityButton.setText(QCoreApplication.translate("MainWindow", u"Low", None))
        self.mediumQualityButton.setText(QCoreApplication.translate("MainWindow", u"Medium", None))
        self.highQualityButton.setText(QCoreApplication.translate("MainWindow", u"High", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Countdown Timer", None))
        self.threeSecondsButton.setText(QCoreApplication.translate("MainWindow", u"3 seconds", None))
        self.fiveSecondsButton.setText(QCoreApplication.translate("MainWindow", u"5 second", None))
        self.tenSecondsButton.setText(QCoreApplication.translate("MainWindow", u"10 second", None))
        self.noneTimerButton.setText(QCoreApplication.translate("MainWindow", u"None", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingsTab), QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

