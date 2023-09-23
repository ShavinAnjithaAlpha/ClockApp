import sys, math, os, sqlite3, pygame
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QAction, QGroupBox, QTabWidget, QVBoxLayout,
                             QHBoxLayout, QSpacerItem, QSystemTrayIcon, QMenu, QStyle, QScrollArea, QSizePolicy,
                             QLineEdit, QCheckBox, QInputDialog, QDialog, QFrame, QMessageBox, QStackedLayout)
from PyQt5.QtCore import Qt, QSize, QSizeF,QTime, QTimer, QDateTime, QDate,QPoint, QPointF, QRect, QRectF, QEasingCurve,QPropertyAnimation
from PyQt5.QtGui import QColor, QIcon, QFont, QPalette, QPainter, QPen, QBrush, QPixmap
from PyQt5.QtMultimedia import QSound

class AlarmWidget(QWidget):
    def __init__(self, id, time = "00:00 AM"):
        super(AlarmWidget, self).__init__()

        self.time = time
        self.id = id
        self.database_file = "alarm/alarm.db"
        self.initializeUI()

    def initializeUI(self):

        self.initial_width = self.width()
        self.initial_height = self.height()

        # create the time label and the on off check box
        self.time_display_label = QLabel(self.time)
        self.time_display_label.setFont(QFont('Helvetica [Cronyx]', 30))

        self.OnOffCheckBox = QCheckBox("On/Off")
        self.OnOffCheckBox.setStyleSheet("""
                                    color : rgb(60, 60, 60);
                                    font-size : 12px""")
        self.OnOffCheckBox.setObjectName("check_box")
        self.OnOffCheckBox.stateChanged.connect(self.changeOnOff)

        # create the label field
        self.alarm_label = QLabel("label")
        self.alarm_label.setStyleSheet("""
                                        color : rgb(80, 80 ,80);
                                        font-size : 18px""")

        self.set_label_button = QPushButton("set label")
        self.set_label_button.setObjectName("set_label_button")
        self.set_label_button.pressed.connect(self.setLabel)
        self.set_label_button.setVisible(False)

        # create the delete button
        self.delete_button = QPushButton("delete")
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setVisible(False)
        self.delete_button.pressed.connect(self.deleteAlarm)

        # scroll up button
        self.scroll_up_button = QPushButton()
        self.scroll_up_button.setIcon(QIcon("images/scroll_up.png"))
        self.scroll_up_button.setObjectName("scroll_up")
        self.scroll_up_button.pressed.connect(lambda e=True : self.setVisibleOther(e))
        #scroll down button
        self.scroll_down_button = QPushButton()
        self.scroll_down_button.setIcon(QIcon("images/scroll_down.png"))
        self.scroll_down_button.setObjectName("scroll_down")
        self.scroll_down_button.setVisible(False)
        self.scroll_down_button.pressed.connect(lambda e=False : self.setVisibleOther(e))

        # create the week days button group
        self.days_of_week = {1 : "Mo", 2 : "Tu", 3 : "We", 4 : "Th", 5 : "Fr", 6 : "Sa", 7 : "Su"}
        self.days_buttons = []
        h_box_days = QHBoxLayout()
        for i in range(7):
            day_button = QPushButton(list(self.days_of_week.values())[i])
            day_button.setCheckable(True)
            day_button.clicked.connect(self.changeDaysSettings)
            day_button.setObjectName("day_button")
            day_button.setVisible(False)
            h_box_days.addWidget(day_button)
            self.days_buttons.append(day_button)

        # create the h box for pack the time label and check box
        h_box1 = QHBoxLayout()
        h_box1.addWidget(self.time_display_label)
        h_box1.addStretch(5)
        h_box1.addWidget(self.OnOffCheckBox)

        h_box2 = QHBoxLayout()
        h_box2.addWidget(self.set_label_button)
        h_box2.addWidget(self.delete_button)
        h_box2.addStretch(5)
        h_box2.addWidget(self.scroll_down_button)

        h_box3 = QHBoxLayout()
        h_box3.addStretch(6)
        h_box3.addWidget(self.scroll_up_button)

        # create hte main v box for pack the all fo widget and layouts
        v_box = QVBoxLayout()

        v_box.addWidget(self.alarm_label, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addLayout(h_box1)
        v_box.addLayout(h_box3)
        v_box.addLayout(h_box_days)
        v_box.addLayout(h_box2)

        spacer_item = QSpacerItem(1, 1 ,QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        v_box.addItem(spacer_item)

        self.setLayout(v_box)
        self.setObjectName("main")
        style_sheet = """
                        
                        QCheckBox#check_box::indicator {background-color : red;
                                                        border-radius : 2px;
                                                        min-width : 12px;
                                                        min-height : 12px}
                        QCheckBox#check_box::indicator:checked {background-color : rgb(0, 200, 50)}
                        
                        QPushButton#day_button {background-color : rgb(50, 50, 50);
                                                border-radius : 18px;
                                                color : white;
                                                padding : 5px;
                                                max-width : 24px;
                                                height : 24px;
                                                font-size : 16px;
                                                border : 2px solid rgb(50, 50, 50)}
                        QPushButton#day_button:!checked {background-color : rgb(0, 0 ,0)}
                        QPushButton#day_button:checked {background-color : rgb(50, 50 , 50)}
                        
                        QPushButton#delete_button, QPushButton#set_label_button 
                                                    {background-color : rgb(30, 30 ,30);
                                                    border-radius : 3px;
                                                    padding : 5px;
                                                    font-size : 14px}
                        QPushButton#delete_button:hover, QPushButton#set_label_button:hover 
                                                        {background-color : rgb(65, 65, 65)}
                        QPushButton#delete_button:pressed, QPushButton#set_label_button:pressed 
                                                    {background-color : rgb(100, 100, 100)}
                        QPushButton#scroll_up {background-color : rgb(30, 30, 30);
                                                border-radius : 2px;
                                                font-size : 13px}
                        QPushButton#scroll_down {background-color : rgb(30, 30, 30);
                                                border-radius : 2px;
                                                font-size : 13px}
                        """
        self.setStyleSheet(style_sheet)

    def setLabel(self):

        # open the text input dialog box and get the text
        text, ok = QInputDialog.getText(self, "Label Text", "label : ")

        if ok:
            self.alarm_label.setText(text)

            # save the new tex to database file
            con = sqlite3.connect(self.database_file)
            cursor = con.cursor()

            if self.id[-1] == "d":
                db_id = self.id.replace("d", "")
                cursor.execute(f"""UPDATE defualt_alarm_table SET label='{text}' WHERE id={db_id}""")
            else:
                db_id = self.id.replace("u", "")
                cursor.execute(f"""UPDATE alarm_table SET label='{text}' WHERE id={db_id}""")

            # save the above changes
            con.commit()

    def deleteAlarm(self):

        if self.id[-1] == "d":
            QMessageBox.warning(self, "Alarm delete Dialog Box", "Default Alarm cannot be delete/remove")
        else:
            msg = QMessageBox.question(self, "Alarm delete Dialog", "Are you sure to delete this Alarm?",
                                    QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)

            if msg == QMessageBox.StandardButton.Yes:
                # delete the alarm from the alarm table
                # create hte connection with the database
                con = sqlite3.connect(self.database_file)
                cursor = con.cursor()

                alarm_id = self.id.replace("u", "")
                cursor.execute(f""" DELETE FROM alarm_table WHERE id={alarm_id} """)
                # save the changes
                con.commit()
                con.close()

                # delete the alarm widget
                self.deleteLater()

    def setVisibleOther(self, bool):
        if bool:

            # create the animation to visible to the ivisible widgets
            self.anim = QPropertyAnimation(self, b"size")
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.initial_width , self.initial_height = self.width(), self.height()
            self.anim.setEndValue(QSizeF(self.initial_width, self.initial_height*1.5))
            self.anim.setDuration(1000)

            self.scroll_up_button.setVisible(False)
            self.anim.start()

            for b in self.days_buttons:
                b.setVisible(True)
            for w in [self.delete_button, self.set_label_button, self.scroll_down_button]:
                w.setVisible(True)



        else:
            # create the animation to visible to the ivisible widgets
            self.anim = QPropertyAnimation(self, b"size")
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.anim.setEndValue(QSizeF(self.initial_width, self.initial_height))
            self.anim.setDuration(1000)

            self.scroll_up_button.setVisible(True)
            self.anim.start()

            for b in self.days_buttons:
                b.setVisible(False)
            for w in [self.delete_button, self.set_label_button, self.scroll_down_button]:
                w.setVisible(False)

    def setDays(self, days_text):

        # analyse the days_text and generate the new days list
        day_list = days_text.split(",")

        for i in range(len(self.days_buttons)):
            if str(i+1) in day_list:
                self.days_buttons[i].setChecked(True)
            else:
                self.days_buttons[i].setChecked(False)

    def changeDaysSettings(self):

        # generate the days text
        days_text = ""
        for i, button in enumerate(self.days_buttons):
            if button.isChecked():
                days_text += ",{}".format(i+1)

        # create the connection
        con = sqlite3.connect(self.database_file)
        cursor = con.cursor()

        if self.id[-1] == "d":
            db_id = self.id.replace("d", "")
            cursor.execute(f"""UPDATE defualt_alarm_table SET days='{days_text}' WHERE id={db_id}""")
        else:
            db_id = self.id.replace("u", "")
            cursor.execute(f"""UPDATE alarm_table SET days='{days_text}' WHERE id={db_id}""")
        # save the changes
        con.commit()

    def changeOnOff(self, state):

        if state:
            i = 1
        else:
            i = 0

        # create the connection to database file
        con = sqlite3.connect(self.database_file)
        cursor = con.cursor()

        if self.id[-1] == "d":
            db_id = self.id.replace("d", "")
            cursor.execute(f"""UPDATE defualt_alarm_table SET on_off={i} WHERE id={db_id}""")
        else:
            db_id = self.id.replace("u", "")
            cursor.execute(f"""UPDATE alarm_table SET on_off={i} WHERE id={db_id}""")

        # save the changes
        con.commit()

    def setOnOff(self, bool : int):

        if bool == 1:
            self.OnOffCheckBox.setCheckState(Qt.CheckState.Checked)
            self.time_display_label.setStyleSheet("""color : rgb(0, 80, 150)""")
        else:
            self.OnOffCheckBox.setCheckState(Qt.CheckState.Unchecked)
            self.time_display_label.setStyleSheet("color : rgb(205, 205, 205)")

class TimeCircleWidget(QWidget):
    def __init__(self):
        super(TimeCircleWidget, self).__init__()

        # declare the variables to manage the time of the widget
        self.timer_time = 0
        self.current_time = 0
        self.time_fraction = 0
        # defined the etxt color
        self.display_color = QColor(0, 120, 220)
        self.sign_text = "+"

        self.setFixedSize(250, 250)
        self.show()

    def paintEvent(self, event):

        # create the painter object
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # start the paint , start the painter object
        painter.begin(self)

        circle_radius = self.width()*0.4
        # draw the main circle
        pen_new = QPen(QColor(150, 150, 150), 3)
        painter.setPen(pen_new)
        painter.drawEllipse(QPoint(self.width()/2, self.height()/2), circle_radius, circle_radius)

        # create the time line arc
        # set the pen first
        pen_new = QPen(self.display_color, 4)
        painter.setPen(pen_new)
        painter.drawArc(QRect(self.width()/2-circle_radius, self.height()/2 - circle_radius
                              , 2*circle_radius, 2*circle_radius), 90*16, -360*self.time_fraction * 16)

        # calculate the small circle center position
        center_x = self.width()/2 + circle_radius*math.sin(math.radians(360*self.time_fraction))
        center_y = self.height()/2 - circle_radius*math.cos(math.radians(360*self.time_fraction))
        # create the time line small circle
        small_circle_radius = 4
        painter.setPen(pen_new)
        painter.setBrush(QBrush(self.display_color))
        painter.drawEllipse(QPointF(center_x, center_y), small_circle_radius, small_circle_radius)

        # get the time text from the get timetext fucntion
        time_text = self.getTimeText(self.current_time)

        # determine the size of font of the time text consider the time text length
        if len(time_text) <= 2:
            font_size = 65
        elif len(time_text) <= 5:
            font_size = 45
        else:
            font_size = 25
        if self.sign_text == "-":
            time_text = "-{}".format(time_text)
        # create the time text
        pen_new = QPen(self.display_color, 4)
        painter.setPen(pen_new)
        painter.setFont(QFont('Helvetica [Cronyx]', font_size))
        painter.drawText(QRectF(self.width()/2 - circle_radius*0.8, self.height()/2-circle_radius*0.4, circle_radius*1.6, circle_radius*0.8),
                                            Qt.AlignmentFlag.AlignCenter, time_text)

        painter.end()
        self.update()

    def setTimerTime(self, time_value):

        self.timer_time = time_value
        self.current_time = time_value
        self.time_fraction = 0
        self.repaint()

        self.current_time = 0

    def setCurrentTime(self, time_value):

        self.current_time = time_value
        if self.current_time >= self.timer_time:
            self.current_time -= self.timer_time

        self.time_fraction = self.current_time/self.timer_time

        self.repaint()

    def getTimeText(self, time_value):

        # get time text as the list
        time_text_list = self.convertToTime(int(time_value))

        if time_text_list[1] == 0 and time_text_list[0] == 0:
            return "{:02d}".format(time_text_list[2])
        elif time_text_list[0] == 0 and time_text_list[1] != 0:
            return "{:02d}:{:02d}".format(time_text_list[1], time_text_list[2])
        elif time_text_list[0] != 0:
            return "{:02d}:{:02d}:{:02d}".format(time_text_list[0], time_text_list[1], time_text_list[2])

    def convertToTime(self, timeAsmiliSecond: int):

        minute_text = 0
        second_text = 0
        milisecond_text = 0

        secondValue = abs(timeAsmiliSecond) // 1000
        hour_text = secondValue // (60 * 60)
        rest_time = secondValue - hour_text * 60 * 60
        minute_text = rest_time // 60
        second_text = secondValue % 60
        milisecond_text = timeAsmiliSecond - secondValue * 1000

        return (hour_text, minute_text, second_text, milisecond_text)

    def setColor(self, color : QColor):

        self.display_color = color

    def setSign(self, sign_text):

        self.sign_text = sign_text

class TimeLineWidget(QWidget):
    def __init__(self):
        super(TimeLineWidget, self).__init__()

        # declare the fraction varable to manag ethe time line
        self.time_line_fraction = 0

    def setFraction(self, fraction):

        self.time_line_fraction = fraction
        # repaint the widget for new time line fraction
        self.repaint()
        self.update()

    def paintEvent(self, event):

        # create hte instance painter object for paint the widget
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)
        # start the painter
        painter.begin(self)

        # create the main dot line for full time line
        pen_new = QPen(QColor(255, 255, 255), 1)
        pen_new.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen_new)
        painter.drawLine(self.width()*0.1, self.height()/2, self.width()*0.9, self.height()/2)


        # calculate the green color line length
        new_l = self.width()*0.8*self.time_line_fraction
        # create the changable time line use color as the light green
        pen_new = QPen(QColor(0, 240, 80), 2)
        painter.setPen(pen_new)
        painter.drawLine(self.width()*0.1, self.height()/2, self.width()*0.1 + new_l, self.height()/2)

        radius = 4
        # calculate the circle center and the radius
        center_x, center_y = self.width()*0.1 + new_l, self.height()/2
        # create the circle
        brush = QBrush(QColor(0, 240, 80))
        painter.setPen(pen_new)
        painter.setBrush(brush)
        painter.drawEllipse(QPoint(center_x, center_y), radius*1.2, radius)

        # end of the painter
        painter.end()

class reduceTimeWidget(QWidget):

    def __init__(self):
        super(reduceTimeWidget, self).__init__()
        self.initializeUI()

    def initializeUI(self):

        # create the text label for display the current time
        self.time_label = QLabel("00:00:00")
        self.time_label.setFont(QFont('Helvetica [Cronyx]', 50))
        self.time_label.setStyleSheet("""
                                        background-color : rgb(30, 30, 30);
                                        color : white
                                        """)

        # declare the time variable to set the widget current time as the miliseconds
        self.time_value = 0
        self.timer_time = 0

        # create the new widget for paint  the time line as the graphic animated image
        self.time_line_widget = TimeLineWidget()
        self.time_line_widget.setFixedWidth(600)
        self.time_line_widget.setFixedHeight(100)
        # initiate the time line graphics


        # create the v box for pack the all of the widgets
        v_box = QVBoxLayout()

        v_box.addWidget(self.time_label, alignment=Qt.AlignHCenter)
        v_box.addWidget(self.time_line_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(v_box)
        self.show()

    def setCurrentTime(self, new_time):

        self.time_value = new_time
        # convert the new time to time string
        converted_time = self.convertToTime(self.time_value)

        self.time_label.setText("{:02d}:{:02d}".format(converted_time[1], converted_time[2]))

        # update hte time line widget
        fraction = (self.timer_time - self.time_value)/self.timer_time
        # calculate the new time fraction
        self.time_line_widget.setFraction(fraction)

    def setTimerTime(self, time_value):

        self.timer_time = time_value
        # display the time text in the time label
        convert_time = self.convertToTime(self.timer_time)
        self.time_label.setText("{:02d}:{:02d}".format(convert_time[1], convert_time[2]))

    def convertToTime(self, timeAsmiliSecond : int):

        minute_text = 0
        second_text = 0
        milisecond_text = 0

        secondValue = timeAsmiliSecond//1000
        hour_text = secondValue//(60*60)
        rest_time = secondValue - hour_text*60*60
        minute_text = rest_time//60
        second_text = secondValue%60
        milisecond_text = timeAsmiliSecond - secondValue*1000

        return (hour_text, minute_text, second_text, milisecond_text)

    def getTimeText(self, time_value):

        # get time text as the list
        time_text_list = self.convertToTime(time_value)

        if time_text_list[1] == 0:
            return "{:02d}".format(time_text_list[2])
        elif time_text_list[2] == 0:
            return "{:02d}:{:02d}".format(time_text_list[1], time_text_list[2])
        else:
            return "{:02d}:{:02d}:{:02d}".format(time_text_list[0], time_text_list[1], time_text_list[2])

class LapTimeWidget(QWidget):
    def __init__(self, number, lap_time, original_time):
        super(LapTimeWidget, self).__init__()
        self.number = number
        self.lap_time = lap_time
        self.original_time = original_time

        self.initializeUI()

    def initializeUI(self):

        # create the three labels for packthe number ,lap_time and original time
        self.number_label = QLabel("#{}".format(self.number))
        self.number_label.setStyleSheet("""
                                            background-color : rgb(30, 30, 30);
                                            color : rgb(120, 120, 120);
                                            font-size  : 15px""")

        self.lap_time_label = QLabel(self.lap_time)
        self.lap_time_label.setStyleSheet("""
                                        background-color : rgb(30, 30, 30);
                                        color : white;
                                        font-size : 13px""")

        self.original_time_label = QLabel(self.original_time)
        self.original_time_label.setStyleSheet("""
                                                background-color : rgb(30, 30, 30);
                                                color : white;
                                                font-size: 13px""")

        # create the h box for pack the three labels
        h_box = QHBoxLayout()
        h_box.setSpacing(15)

        h_box.addWidget(self.number_label)
        h_box.addWidget(self.lap_time_label)
        h_box.addWidget(self.original_time_label)

        self.setLayout(h_box)

    def setLapTime(self, new_lap_time):

        self.lap_time = new_lap_time
        self.lap_time_label.setText(self.lap_time)

    def setOriginalTime(self, new_original_time):

        self.original_time = new_original_time
        self.original_time_label.setText(new_original_time)

class ShavTime(QWidget):

    def __init__(self):
        super(ShavTime, self).__init__()
        self.initializeUI()

    def initializeUI(self):

        self.setWindowTitle("ShavMinf Time - version 2021.0.0")
        self.setGeometry(250, 250, 600, 500)
        # hide the window title bar
        self.setWindowFlag(Qt.WindowType.WindowShadeButtonHint)

        # create hte three timer for update date ,time and set to the stop watch and the timer
        self.datetime_timer = QTimer()
        self.stopwatch_timer = QTimer()
        self.timer_timer = QTimer()
        self.alarm_timer = QTimer()

        self.setUpWidgets()
        self.SystemTrayCreate()

        # connect the function to the above timer for appropriate processes
        self.datetime_timer.timeout.connect(self.updateDateTime)
        self.stopwatch_timer.timeout.connect(self.updateStopWatch)
        self.timer_timer.timeout.connect(self.updateTimerTimer)
        self.alarm_timer.timeout.connect(self.alarmTimerUpdate)

        # initialte the pygame mixer module
        pygame.mixer.init()
        # show the window in the screen
        self.show()

    def setUpWidgets(self):

        # create the tab bar to the classified the operations
        self.tab_bar = QTabWidget(self)

        # create the widget area for above operations
        self.datetime_widget = QWidget()
        self.stopwatch_widget = QWidget()
        self.timer_widget = QWidget()
        self.alarm_widget = QWidget()
        self.tasks_widget = QWidget()

        # add the this widgets to the tab bar
        tab_bar_titles = ["Time", "StopWatch", "Timer", "Alarm", "Tasks Bar"]
        for i, widget in enumerate([self.datetime_widget, self.stopwatch_widget, self.timer_widget, self.alarm_widget, self.tasks_widget]):
            self.tab_bar.addTab(widget, tab_bar_titles[i])

        # create the v boc for pack the tab bar
        v_box = QVBoxLayout()
        v_box.addWidget(self.tab_bar)

        # create the main widget
        main_widget = QWidget()
        main_widget.setLayout(v_box)
        # create the alarm showing widget
        alarm_showing_widget = QWidget()
        self.alarm_showing_v_box = QVBoxLayout()
        alarm_showing_widget.setLayout(self.alarm_showing_v_box)
        # create the stack pane for program alarm managing
        self.stack_lyt = QStackedLayout()
        self.stack_lyt.addWidget(main_widget)
        self.stack_lyt.addWidget(alarm_showing_widget)

        self.setLayout(self.stack_lyt)
        self.createAlarmShowingWidget()

        # call to the function to create above widget operations
        self.createDateTimeWidget()
        self.createStopWatchWidget()
        self.createTimerWidget()
        self.createAlarmWidget()
        self.createTaskBarWidget()

        # create the Frame widget for display the tab icon info bar
        self.frame_icons = QFrame()
        self.frame_icons.setFixedSize(QSize(self.width(), 60))
        self.frame_icons.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_icons.setStyleSheet("background-color : rgb(5, 5, 5)")
        self.frame_icons.setContentsMargins(2, 2, 2 ,2)
        self.frame_icons.setLineWidth(2)
        self.frame_icons.setMidLineWidth(5)
        self.frame_icons.setFrameShadow(QFrame.Shadow.Raised)
        # create the frame v box for pack the label
        frame_lyt= QVBoxLayout()
        self.frame_icons.setLayout(frame_lyt)

        # get the tab current index
        self.tab_index = self.tab_bar.currentIndex()
        self.tab_icon_label = QLabel()
        self.tab_icon_label.setFixedSize(QSize(45, 45))
        frame_lyt.addWidget(self.tab_icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # set the current tab item
        self.setTabIcon(self.tab_index)

        v_box.addWidget(self.frame_icons, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.tab_bar.currentChanged.connect(self.setTabIcon)

    def setTabIcon(self, tab_index):

        if tab_index == 0:
            self.tab_icon_label.setPixmap(QPixmap("images/clock.png").scaled(self.tab_icon_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        elif tab_index == 1:
            self.tab_icon_label.setPixmap(
                QPixmap("images/stopwatch.png").scaled(self.tab_icon_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
        elif tab_index == 2:
            self.tab_icon_label.setPixmap(
                QPixmap("images/timer.png").scaled(self.tab_icon_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))

        elif tab_index == 3:
            self.tab_icon_label.setPixmap(QPixmap("images/alarm.png").scaled(self.tab_icon_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def createAlarmShowingWidget(self):

        # create the alarm stop button
        alarm_stop_button = QPushButton("Alarm Catching...")
        alarm_stop_button.setStyleSheet("""
                                        QPushButton {background-color : none;
                                                    border-radius : 5px;
                                                    padding : 10px;
                                                    font-size : 17px;
                                                    color : white;
                                                    border : 1px solid rgb(80, 80, 80);
                                                    width : 150px}
                                        QPushButton:hover , QPushButton:pressed {border : 2px solid rgb(120, 120, 120)}""")
        alarm_stop_button.pressed.connect(self.stopAlarm)

        # create the alarm ringing label
        alarm_ringing_label = QLabel("Alarm Ringing...")
        alarm_ringing_label.setStyleSheet("""
                                            color : white;
                                            font-family : Helvetica;
                                            font-size  : 40px;""")

        # aranging the label and button in to the layout
        self.alarm_showing_v_box.addStretch(1)
        self.alarm_showing_v_box.addWidget(alarm_ringing_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.alarm_showing_v_box.addWidget(alarm_stop_button)
        self.alarm_showing_v_box.addStretch(2)

    def createDateTimeWidget(self):

        """ show the current date and time in the window """

        current_time = QTime.currentTime().toString("hh:mm:ss A")
        current_date = QDate.currentDate().toString("dd MMMM yyyy")

        # display the current time and date as the label on this widget
        self.current_date_label = QLabel(current_date)
        self.current_date_label.setFont(QFont("Helvetica [Cronyx]", 24))
        self.current_date_label.setObjectName("currentDateLabel")

        self.current_time_label = QLabel(current_time)
        self.current_time_label.setFont(QFont("Helvetica [Cronyx]" ,45))
        self.current_time_label.setObjectName("currentTimeLabel")

        # create the v box to pakck this labels
        v_box = QVBoxLayout()

        v_box.addStretch(2)
        v_box.addWidget(self.current_time_label, alignment=Qt.AlignHCenter)
        v_box.addWidget(self.current_date_label, alignment=Qt.AlignHCenter)
        v_box.addStretch(3)

        self.datetime_widget.setLayout(v_box)

        # initiate the date time timer by one second
        self.datetime_timer.start(1000)

    def createStopWatchWidget(self):

        # declare the variable to stop watch
        self.stopwatchTime = 0

        # list and time variable to setup the lap timing process
        self.lap_time_widgets = []
        self.lap_time_var = 0

        # create the h box for buttons
        h_box_buttons = QHBoxLayout()

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.setVisible(False)
        self.reset_button.pressed.connect(self.resetStopWatch)

        self.start_button = QPushButton()
        self.start_button.setIcon(QIcon("images/start_button_logo.png"))
        self.start_button.setIconSize(QSize(65, 65))
        self.start_button.setObjectName("start_button")
        self.start_button.setVisible(True)
        self.start_button.pressed.connect(self.startStopWatch)

        self.lap_button = QPushButton("Lap")
        self.lap_button.setObjectName("lap_button")
        self.lap_button.setVisible(False)
        self.lap_button.pressed.connect(self.lapTimeUpdate)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon("images/stop_button_logo.png"))
        self.stop_button.setIconSize(QSize(65, 65))
        self.stop_button.setVisible(False)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.pressed.connect(self.stopStopWatch)

        # pack the button sto the h box
        h_box_buttons.addStretch(1)
        h_box_buttons.addWidget(self.reset_button)
        h_box_buttons.addStretch(2)
        h_box_buttons.addWidget(self.start_button)
        h_box_buttons.addWidget(self.stop_button)
        h_box_buttons.addStretch(2)
        h_box_buttons.addWidget(self.lap_button)
        h_box_buttons.addStretch(1)

        # create the other v box for save the labels
        self.v_box_lap_time_label = QVBoxLayout()
        self.v_box_lap_time_label.setSpacing(3)

        # create the spacer item to manage the area managment of the layout
        spacer_item = QSpacerItem(1, 1 ,QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.v_box_lap_time_label.addItem(spacer_item)

        # widget for the container to te lap time lyt
        self.lap_time_widget = QWidget()
        self.lap_time_widget.setLayout(self.v_box_lap_time_label)

        # create the scroll area to set to the lap time labels
        self.lap_time_scroll_area = QScrollArea()
        self.lap_time_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.lap_time_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lap_time_scroll_area.setWidgetResizable(True)
        self.lap_time_scroll_area.setWidget(self.lap_time_widget)
        self.lap_time_scroll_area.setMinimumHeight(150)
        self.lap_time_scroll_area.setStyleSheet("""border-radius : 5px;
                                                    border-color : rgb(30, 30 ,30)""")

        # create the timer label
        self.stop_watch_text_label = QLabel()
        self.stop_watch_text_label.setText("00:00:00")
        self.stop_watch_text_label.setFont(QFont('Helvetica [Cronyx]', 53))

        # create the main v box for pack the other layouts
        main_v_box = QVBoxLayout()

        main_v_box.addStretch(1)
        main_v_box.addWidget(self.stop_watch_text_label, alignment=Qt.AlignHCenter)
        main_v_box.addWidget(self.lap_time_scroll_area)
        main_v_box.addStretch(1)
        main_v_box.addLayout(h_box_buttons)
        main_v_box.addStretch(1)

        self.stopwatch_widget.setLayout(main_v_box)

    def startStopWatch(self):

        # initiate the stopwatch timer to initiate the stop watch
        self.stopwatch_timer.start(10)

        # set visible to buttons
        self.start_button.setVisible(False)
        self.stop_button.setVisible(True)
        self.lap_button.setVisible(True)
        self.reset_button.setVisible(True)

    def stopStopWatch(self):
        # stop the stop watch timer
        self.stopwatch_timer.stop()

        # set visible appropriate buttons
        self.start_button.setVisible(True)
        self.stop_button.setVisible(False)
        self.lap_button.setVisible(False)
        self.reset_button.setVisible(True)

    def resetStopWatch(self):
        # stop the stop watch
        self.stopwatch_timer.stop()

        # set the stop watcj time to zero vlaue
        self.stopwatchTime = 0
        self.stop_watch_text_label.setText("00:00:00")

        # set the start button only visible
        self.start_button.setVisible(True)
        self.stop_button.setVisible(False)
        self.lap_button.setVisible(False)
        self.reset_button.setVisible(False)

        # empty the lap time widget list and clear the scroll area
        for w in self.lap_time_widgets:
            w.setVisible(False)

        self.lap_time_widgets = []
        self.lap_time_var = 0

    def lapTimeUpdate(self):

        # set the lap time var to zero
        self.lap_time_var = 0

        # create the new lap time widget and append to the laptime widget list
        new_lap_time_widget = LapTimeWidget((len(self.lap_time_widgets) + 1), "00:00:00", self.stop_watch_text_label.text())
        self.lap_time_widgets.append(new_lap_time_widget)

        self.v_box_lap_time_label.insertWidget(0, new_lap_time_widget, alignment=Qt.AlignHCenter)

    def updateStopWatch(self):

        # increase the value of the stop watch time variable
        self.stopwatchTime += 10
        self.lap_time_var += 10

        # set the text of the stop watch label
        convert_time = self.convertToTime(self.stopwatchTime)
        self.stop_watch_text_label.setText("{:02d}:{:02d}:{:02d}".format(convert_time[1], convert_time[2], int(convert_time[3]/10)))

        # if lap time widget list in not empty update the list last item time for time outs
        if self.lap_time_widgets != []:
            # set the list last item time to new time
            self.lap_time_widgets[-1].setOriginalTime(self.stop_watch_text_label.text())
            lap_time_converted = self.convertToTime(self.lap_time_var)

            self.lap_time_widgets[-1].setLapTime("%02d:%02d:%02d"%(lap_time_converted[1], lap_time_converted[2], lap_time_converted[3]/10))


    def createTimerWidget(self):

        # create the buttons for timer widget
        self.timer_start_button = QPushButton()
        self.timer_start_button.setObjectName("start_button2")
        self.timer_start_button.setIcon(QIcon("images/start_button_logo.png"))
        self.timer_start_button.setIconSize(QSize(65, 65))
        self.timer_start_button.setVisible(False)
        self.timer_start_button.pressed.connect(self.start_timer_timer)

        self.timer_addtimer_button = QPushButton("Add Timer")
        self.timer_addtimer_button.setObjectName("addtimer_button")
        self.timer_addtimer_button.setVisible(True)
        self.timer_addtimer_button.pressed.connect(self.setNewTimer)

        self.timer_stop_button = QPushButton()
        self.timer_stop_button.setObjectName("stop_button2")
        self.timer_stop_button.setIcon(QIcon("images/stop_button_logo.png"))
        self.timer_stop_button.setIconSize(QSize(65, 65))
        self.timer_stop_button.setVisible(False)
        self.timer_stop_button.pressed.connect(self.stop_timer_timer)

        self.timer_delete_button = QPushButton("delete")
        self.timer_delete_button.setObjectName("timer_delete_button")
        self.timer_delete_button.setVisible(False)
        self.timer_delete_button.pressed.connect(self.timer_delete)

        # create the label for diaplay the timer time text
        #self.timer_time_label = QLabel("00:00:00")
        #self.timer_time_label.setFont(QFont('Helvetica [Cronyx]', 50))
        self.timer_time_label = TimeCircleWidget()

        # entry box for get the time  value
        self.timer_addtime_entry = QLineEdit()
        self.timer_addtime_entry.setFont(QFont('Helvetica [Cronyx]', 25))
        self.timer_addtime_entry.setFixedSize(350, 50)
        self.timer_addtime_entry.setVisible(False)
        self.timer_addtime_entry.textChanged.connect(self.changeNewTimer)
        self.timer_addtime_entry.setStyleSheet(""" 
                                            border : 3px solid rgb(240, 50, 6);
                                            border-radius : 4px""")
        self.timer_addtime_entry.returnPressed.connect(self.start_timer_timer)

        # declare the time variable to update the timer label
        self.timer_time_var = 0

        # create the h box for pack the buttons
        h_box = QHBoxLayout()
        h_box.addStretch(1)
        h_box.addWidget(self.timer_delete_button)
        h_box.addStretch(2)
        h_box.addWidget(self.timer_start_button)
        h_box.addWidget(self.timer_stop_button)
        h_box.addStretch(2)
        h_box.addWidget(self.timer_addtimer_button)
        h_box.addStretch(1)

        # create the v box for pack the all of widget to the timer widget
        v_box = QVBoxLayout()
        v_box.addStretch(1)
        v_box.addWidget(self.timer_time_label, alignment=Qt.AlignHCenter)
        v_box.addWidget(self.timer_addtime_entry, alignment=Qt.AlignHCenter)
        v_box.addStretch(2)
        v_box.addLayout(h_box)
        v_box.addStretch(1)

        self.timer_widget.setLayout(v_box)

    def setNewTimer(self):

        # first stop the timer object for timer widget
        self.timer_timer.stop()
        # show the time edit entry field
        self.timer_addtime_entry.setVisible(True)
        self.timer_addtime_entry.setFocus()
        self.timer_addtimer_button.setVisible(False)
        self.timer_stop_button.setVisible(False)
        self.timer_start_button.setVisible(True)
        self.timer_delete_button.setVisible(False)

    def changeNewTimer(self, text):

        if self.timer_addtime_entry.text() != "":
            # get the entry boc value
            self.timer_time_var = int(self.timer_addtime_entry.text()) * 1000
            # convert the time to original time text
            self.timer_time_label.setTimerTime(self.timer_time_var)
        else:
            self.timer_time_var = 0

        self.timer_time_label.setColor(QColor(0, 120 ,220))
        self.timer_time_label.setSign("+")

    def start_timer_timer(self):

        self.timer_timer.start(100)
        self.timer_start_button.setVisible(False)
        self.timer_stop_button.setVisible(True)
        self.timer_delete_button.setVisible(True)
        self.timer_addtime_entry.setVisible(False)
        self.timer_addtimer_button.setVisible(True)
        # focus to the entry box
        self.timer_addtime_entry.setFocus()

    def stop_timer_timer(self):

        self.timer_timer.stop()
        # show the wanted widget and  hide the other widget
        self.timer_start_button.setVisible(True)
        self.timer_stop_button.setVisible(False)

    def timer_delete(self):

        self.timer_timer.stop()
        self.timer_addtime_entry.setVisible(False)
        self.timer_start_button.setVisible(True)
        self.timer_stop_button.setVisible(False)
        self.timer_addtime_entry.setVisible(True)
        self.timer_delete_button.setVisible(False)

    def updateTimerTimer(self):

        # decrease the timer time value by 1000 milisecond
        self.timer_time_var -= 100

        if self.timer_time_var <= 0:
            #self.timer_timer.stop()
            #self.timer_start_button.setVisible(True)
            #self.timer_stop_button.setVisible(False)
            #self.timer_addtime_entry.setVisible(True)
            #self.timer_delete_button.setVisible(False)
            self.timer_time_label.setColor(QColor(220, 10, 0))
            self.timer_time_label.setSign("-")
            self.tray_icon.showMessage("Timer Notification", "timer time ended before {}".format(self.getTimeText(self.timer_time_var)),
                                       QIcon("Time.png"), 10)
        # convert_time = self.convertToTime(self.timer_time_var)
        # self.timer_time_label.setText("{:02d}:{:02d}".format(convert_time[0], convert_time[1]))
        self.timer_time_label.setCurrentTime(self.timer_time_var)



    def createTaskBarWidget(self):
        pass

    def setUpAlarmDatabase(self):

        self.alarm_database_file = "alarm/alarm.db"
        if not(os.path.exists(self.alarm_database_file)):

            # create the connection
            con = sqlite3.connect(self.alarm_database_file)
            # create the cursor object
            cursor = con.cursor()
            cursor.execute("DROP TABLE IF EXISTS alarm_table")
            cursor.execute("""CREATE TABLE alarm_table(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                                                        label TEXT NOT NULL,
                                                        time TEXT NOT NULL,
                                                        days TEXT NOT NULL,
                                                        on_off INTEGER NOT NULL,
                                                        sound_track TEXT NOT NULL
                                                        )""")

            # create the defualt alarm database
            cursor.execute("""CREATE TABLE defualt_alarm_table (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                label TEXT NOT NULL,
                                                                time TEXT NOT NULL,
                                                                days TEXT NOT NULL,
                                                                on_off INTEGER NOT NULL,
                                                                sound_track TEXT NOT NULL)""")

            defualt_alarm_data = {1 : ["08:00 AM", "1,2,3,4,5,6,7", 0],
                                  2 : ["09:00 PM", "1,2,3,4,5,6,7", 0]}

            for alarm in list(defualt_alarm_data.values()):
                cursor.execute(f"""INSERT INTO defualt_alarm_table(label, time, days, on_off, sound_track)
                                    VALUES ('label', '{alarm[0]}', '{alarm[1]}', {alarm[2]}, 'defualt_track.mp4')""")
            # save the this changes
            con.commit()

            print("[INFO] database file create successful...")

    def getDefualtAlarmSettings(self):

        # create hte connection
        con = sqlite3.connect(self.alarm_database_file)
        cursor = con.cursor()

        cursor.execute("""SELECT * FROM defualt_alarm_table """)
        alarm_data_primary = cursor.fetchall()

        secondary_alarm_settings = {}
        for alarm in alarm_data_primary:
            secondary_alarm_settings[alarm[0]] = [alarm[1], alarm[2], alarm[3], alarm[4]]

        return secondary_alarm_settings

    def getAlarmSettings(self):

        # create hte connection
        con = sqlite3.connect(self.alarm_database_file)
        cursor = con.cursor()

        cursor.execute("""SELECT * FROM alarm_table """)
        alarm_data_primary = cursor.fetchall()

        secondary_alarm_settings = {}
        for alarm in alarm_data_primary:
            secondary_alarm_settings[alarm[0]] = [alarm[1], alarm[2], alarm[3], alarm[4]]

        return secondary_alarm_settings

    def createAlarmWidget(self):
        # first set up the alarm database
        self.setUpAlarmDatabase()

        # create the scroll area for pack the alarm widget
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)

        # create the layout for pack the alarm widgets
        scroll_area_widget = QWidget()
        self.v_box_alarm = QVBoxLayout()
        scroll_area_widget.setLayout(self.v_box_alarm)
        scroll_area.setWidget(scroll_area_widget)

        # create the new alarm create button
        new_alarm_button = QPushButton("+")
        new_alarm_button.setObjectName("new_alarm_button")
        new_alarm_button.pressed.connect(self.create_new_user_alarm)

        # create the spacer item and get in to the alarm lyt
        spacer_item = QSpacerItem(1, 1 ,QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.v_box_alarm.addItem(spacer_item)

        v_box1 = QVBoxLayout()
        v_box1.addWidget(scroll_area)
        v_box1.addWidget(new_alarm_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.alarm_widget.setLayout(v_box1)

        # create the default alarms
        self.defualt_alarm_dict = {}
        self.user_alarm_dict = {}
        self.alarm_widgets = []

        # get the defualt alarm settings from database file
        alarm_settings = self.getDefualtAlarmSettings()

        for i, alarm in alarm_settings.items():
            # create the new alarm widget
            alarm_widget = AlarmWidget("{}d".format(i), alarm[1])
            alarm_widget.alarm_label.setText(alarm[0])
            alarm_widget.setDays(alarm[2])
            alarm_widget.setOnOff(alarm[3])
            # pack the alarm widget in the lyt
            self.v_box_alarm.addWidget(alarm_widget)
            self.alarm_widgets.append(alarm_widget)
            # insert data to defualt alarm list
            self.defualt_alarm_dict[i] = alarm

        self.createUserAlarmWidget(self.v_box_alarm)
        # start the alarm timer
        self.alarm_timer.start(5000)

    def createUserAlarmWidget(self, v_box : QVBoxLayout):

        # load the data from the database file to dict list
        self.user_alarm_dict = self.getAlarmSettings()

        for i, alarm in self.user_alarm_dict.items():
            # create the new alarm widget
            alarm_widget = AlarmWidget("{}u".format(i), alarm[1])
            alarm_widget.alarm_label.setText(alarm[0])
            alarm_widget.setDays(alarm[2])
            alarm_widget.setOnOff(alarm[3])
            # pack the alarm widget in the lyt
            v_box.addWidget(alarm_widget)
            self.alarm_widgets.append(alarm_widget)

    def create_new_user_alarm(self):

        # get the user alarm time from the new dialog box
        self.time_dialog = QDialog(self)
        self.time_dialog.setModal(True)
        self.time_dialog.setWindowTitle("New Alarm of User")

        # create the two entry field to get the time from the user
        self.new_alarm_hour_entry = QLineEdit()
        self.new_alarm_minute_entry = QLineEdit()

        self.new_alarm_hour_entry.setObjectName("new_alarm_entry")
        self.new_alarm_minute_entry.setObjectName("new_alarm_entry")

        self.new_alarm_hour_entry.returnPressed.connect(lambda : self.new_alarm_minute_entry.setFocus())

        # create the create and cancel buttons
        create_button = QPushButton("Create")
        cancel_button = QPushButton("Cancel")

        for button in [create_button, cancel_button]:
            button.setStyleSheet("""
                                    QPushButton {background-color : rgb(0, 50, 180);
                                                border-radius : 3px;
                                                padding : 6px;
                                                border : none}
                                    QPushButton:hover, QPushButton:pressed {background-color : rgb(0, 70, 150)}""")


        cancel_button.clicked.connect(self.time_dialog.reject)
        create_button.pressed.connect(self.NewUserAlarm)

        # create the labels
        set_time_label = QLabel("Set time")
        set_time_label.setFont(QFont('Helvetica [Cronyx]', 35))

        minute_label = QLabel("minute")
        hour_label = QLabel("hour")

        for label in [minute_label, hour_label, set_time_label]:
            label.setObjectName("new_alarm_label")

        # create the layout for pack the widgets
        h_box1 = QHBoxLayout()
        h_box1.addWidget(self.new_alarm_hour_entry)
        h_box1.addWidget(QLabel(":"))
        h_box1.addWidget(self.new_alarm_minute_entry)
        h_box1.addStretch(6)

        h_box2 = QHBoxLayout()
        h_box2.addWidget(hour_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        h_box2.addStretch(2)
        h_box2.addWidget(minute_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        h_box2.addStretch(6)

        h_box3 = QHBoxLayout()
        h_box3.addWidget(create_button)
        h_box3.addWidget(cancel_button)

        # create the main v box
        v_box = QVBoxLayout()
        v_box.addWidget(set_time_label, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addStretch(2)
        v_box.addLayout(h_box1)
        v_box.addLayout(h_box2)
        v_box.addLayout(h_box3)

        self.new_alarm_hour_entry.setFocus()
        self.time_dialog.setMinimumSize(250, 250)
        self.time_dialog.setLayout(v_box)
        self.time_dialog.show()

    def NewUserAlarm(self):

        # get the time from the entry fields
        hour, minute = int(self.new_alarm_hour_entry.text()), int(self.new_alarm_minute_entry.text())

        if 0 <= hour <= 23 and 0 <= minute <= 59:

            label = "label"
            days = "1,2,3,4,5,6,7"
            sound_track = "alarm/alarm.mp4"
            time_ob = QTime(hour, minute)
            time_text = time_ob.toString("hh:mm A")

            # create the connection to database file
            con = sqlite3.connect(self.alarm_database_file)
            cursor = con.cursor()

            cursor.execute(f"""INSERT INTO alarm_table(label, time, days, on_off, sound_track)
                                                VALUES ('{label}', '{time_text}', '{days}', 1, '{sound_track}')""")

            con.commit()
            # get the id of the created new alarm field
            cursor.execute(f"""SELECT id FROM alarm_table WHERE time='{time_text}' """)
            id_list = cursor.fetchall()
            alarm_id = int(id_list[0][0])

            # create the new alarm widget
            alarm_widget = AlarmWidget("{}u".format(alarm_id), time_text)
            alarm_widget.setOnOff(1)
            alarm_widget.setDays(days)
            alarm_widget.alarm_label.setText(label)

            # pack the alarm widget to lty
            self.v_box_alarm.addWidget(alarm_widget)
            self.alarm_widgets.append(alarm_widget)
            # append the new alarm to user_alarm_dict
            alarm_list = [label, time_text, days, 1, sound_track]
            self.user_alarm_dict[alarm_id] = alarm_list

            # close the dialog window
            self.time_dialog.close()


        else:
            print("[INFO] hour and minute are invalid...")

    def alarmTimerUpdate(self):

        # get the current time and date
        current_time = QTime.currentTime().toString("hh:mm A")
        current_date = QDate.currentDate().toString("yyyy:mm:dd")

        week_date_id = QDate.currentDate().dayOfWeek()

        for alarm in self.user_alarm_dict.values():
            if alarm[3] == 1:
                # determine if current date is the day of week of the alarm object
                if (str(week_date_id) in alarm[2]) and alarm[1] == current_time:
                    self.alarm_timer.stop()
                    self.tray_icon.showMessage("Alarm Ringing...", "Alalrm time has been coming...", 3000)
                    # switch tot he alarm showing widget
                    self.stack_lyt.setCurrentIndex(1)
                    # play the alarm sound track by the pygame module
                    pygame.mixer.music.load("alarm/alarm.mp3")
                    pygame.mixer.music.play(loops=0)
                    if not pygame.mixer.music.get_busy():
                        # end of the audio playing
                        self.alarm_timer.start(5000)
                        self.stack_lyt.setCurrentIndex(0)

    def stopAlarm(self):

        # change the alarm window stack layout widget
        self.stack_lyt.setCurrentIndex(0)

        # stop the playing of alarm sound track
        pygame.mixer.music.stop()
        # start the alarm timer
        self.alarm_timer.start(5000)



    def updateDateTime(self):

        # get the current time and date from the os
        current_date = QDate.currentDate().toString("dd MMMM yyyy")
        current_time = QTime.currentTime().toString("hh:mm:ss A")

        self.current_date_label.setText(current_date)
        self.current_time_label.setText(current_time)

    def SystemTrayCreate(self):

        # create the system tray icon object to manage that processes
        self.tray_icon = QSystemTrayIcon(QIcon("Time.png"))

        # create the menu for append to the tray bar
        tray_menu = QMenu()

        # create the actions to tray menu
        open_act = QAction("Open", self)
        open_act.triggered.connect(self.show)

        close_act = QAction("Exit", self)
        close_act.triggered.connect(QApplication.quit)

        tray_menu.addAction(open_act)
        tray_menu.addSeparator()
        tray_menu.addAction(close_act)

        # append the tray menu to tray object
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.show()

    def closeEvent(self, event):

        """ Display the message when main window has been closed"""

        self.tray_icon.showMessage("Notification", "ShavTime program is still Running...", 8000)

    def getTimeText(self, time_value):

        # get time text as the list
        time_text_list = self.convertToTime(int(time_value))

        if time_text_list[1] == 0 and time_text_list[0] == 0:
            return "{:02d}".format(time_text_list[2])
        elif time_text_list[0] == 0 and time_text_list[1] != 0:
            return "{:02d}:{:02d}".format(time_text_list[1], time_text_list[2])
        elif time_text_list[0] != 0:
            return "{:02d}:{:02d}:{:02d}".format(time_text_list[0], time_text_list[1], time_text_list[2])

    def convertToTime(self, timeAsmiliSecond: int):

        minute_text = 0
        second_text = 0
        milisecond_text = 0

        secondValue = abs(timeAsmiliSecond) // 1000
        hour_text = secondValue // (60 * 60)
        rest_time = secondValue - hour_text * 60 * 60
        minute_text = rest_time // 60
        second_text = secondValue % 60
        milisecond_text = timeAsmiliSecond - secondValue * 1000

        return (hour_text, minute_text, second_text, milisecond_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Time.png"))
    app.setQuitOnLastWindowClosed(False)

    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Shadow, QColor(25, 25, 25))
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor("white"))
    palette.setColor(QPalette.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor('white'))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(63, 63, 63))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)

    palette.setColor(QPalette.Highlight, QColor(250, 70, 8))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)

    style_sheet = """
                           QWidget {background-color : rgb(30, 30, 30)}

                           QTabWidget {background-color : rgb(30, 30 ,30)}

                           QTabWidget::pane {background-color : rgb(40, 40, 40)}

                           QTabWidget::tab-bar {background-color : rgb(240 ,70, 6);
                                               border-radius : 1px;
                                               border-width : 0px}

                           QTabBar::tab {background-color : rgb(240, 70, 6);
                                       border-radius : 2px;
                                       border-top-right-radius : 10px 10px;
                                       border-bottom-right-radius : 4px 4px;
                                       border-width : 0px;
                                       padding : 5px;
                                       font-size : 12px;
                                       min-width : 100px;
                                       font-family : Helvetica;
                                       color : rgb(10, 10, 10)}

                           QTabBar::tab:selected {background-color : rgb(250, 50 ,6);
                                                   min-width : 120px;
                                                   min-height : 20px;
                                                   border-right-top-radius : 12px 13px;
                                                   border-bottom : 2px solid rgb(0, 200, 50)}

                           QLabel#currentTimeLabel {color : rgb(0, 120 ,240)}

                           QLabel#currentDateLabel {color : white}

                           QPushButton#start_button {background-color : rgb(30, 30, 30);
                                                    color : white;
                                                    font-size : 15px;
                                                    border-radius : 3px;
                                                    padding : 8px}
                            
                                                    
                           QPushButton#reset_button {background-color  :rgb(30, 30, 30);
                                                    color : white;
                                                    border-radius : 3px;
                                                    padding : 7px;
                                                    font-size  :15px;
                                                    min-width : 40px
                                                    }
                           QPushButton#reset_button:hover,pressed {background-color : rgb(50, 50, 50)}
                            
                           QPushButton#lap_button {background-color : rgb(30, 30, 30);
                                                    color: white;
                                                    border-radius : 3px;
                                                    font-size : 15px;
                                                    padding : 7px;
                                                    min-width : 40px}
                           QPushButton#lap_button:hover,pressed {background-color : rgb(50, 50 ,50)}
                           
                           QPushButton#start_button2 {background-color : rgb(30, 30, 30);
                                                    color : white;
                                                    font-size : 15px;
                                                    border-radius : 3px;
                                                    padding : 8px}
                                                    
                           QPushButton#stop_button2 {background-color : rgb(30, 30, 30);
                                                    color : white;
                                                    font-size : 15px;
                                                    border-radius : 3px;
                                                    padding : 8px}
                                                    
                           QPushButton#addtimer_button {background-color : rgb(30, 30, 30);
                                                    color: white;
                                                    border-radius : 3px;
                                                    font-size : 15px;
                                                    padding : 7px;
                                                    min-width : 40px}
                                                    
                           QPushButton#addtimer_button:hover {
                                                            background-color : rgb(50, 50, 50);
                                                    }
                                                    
                           QPushButton#timer_delete_button {background-color : rgb(30, 30, 30);
                                                    color: white;
                                                    border-radius : 3px;
                                                    font-size : 15px;
                                                    padding : 7px;
                                                    min-width : 40px}
                                                    
                           QPushButton#timer_delete_button:hover {
                                                            background-color : rgb(50, 50, 50);
                                                    } 
                           QScrollBar:vertical {background-color : rgb(20, 20 ,20);
                                                max-width : 10px;
                                                border-radius : 5px}
                           QScrollBar::handle:vertical {background-color : rgb(50, 50 ,50);
                                                border-radius : 5px;
                                                margin-top : 0px;
                                                margin-bottom : 0px}
                           QScrollBar::handle:hover {background-color : rgb(0, 120, 240)}
                           QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {background : none;
                                                        border : none}
                           QScrollBar::up-arrow:vertical , QScrollBar::down-arrow:vertical
                                                {background : none;
                                                border : none}
                                                 
                           QPushButton#new_alarm_button {background-color : rgb(0, 120 ,240);
                                                        min-width : 45px;
                                                        min-height : 45px;
                                                        border-radius : 20px;
                                                        color : rgb(30, 30, 30);
                                                        font-size : 20px;
                                                        font-style : bold}
                                                        
                           QPushButton#new_alarm_button:pressed, QPushButton#new_alarm_button:hover 
                                                                {background-color : rgb(0, 140, 240)}
                           
                           QLineEdit#new_alarm_entry {background-color : rgb(30, 30 ,30);
                                                    border-radius : 0px;
                                                    border-bottom : 1px solid white;
                                                    border-top-width : 0px;
                                                    border-left-width : 0px;
                                                    border-right-width : 0px;
                                                    max-width : 45px;
                                                    font-size : 20px}
                          """

    app.setStyleSheet(style_sheet)

    window = ShavTime()
    sys.exit(app.exec_())
