import cv2
from gpiozero import Button, DistanceSensor, Buzzer
from time import sleep
import smtplib

GMAIL_USER = 'enter email'
GMAIL_PASS = 'enter password'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def send_email(recipient, subject, text):
    smtpserver = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(GMAIL_USER, GMAIL_PASS)
    header = f"To:{recipient}\nFrom:{GMAIL_USER}\nSubject:{subject}\n"
    msg = header + "\n" + text + "\n\n"
    smtpserver.sendmail(GMAIL_USER, recipient, msg)
    smtpserver.close()

button = Button(18)
sensor = DistanceSensor(echo=25, trigger=17)
buzzer = Buzzer(23)

def update_reading():
    cm = sensor.distance * 100
    return cm


def buzz(pitch, duration):
    period = 1.0 / pitch
    delay = period / 2
    cycles = int(duration*pitch)
    buzzer.beep(on_time=period,off_time=period,n=int(cycles/2))

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(0)

while True:
    value = update_reading()

    if value <= 20:
        print(f"Motion detected: {value} cm")
        buzz(200, 2)

        ret, frame = cap.read()
        if ret:
            rotated = cv2.rotate(frame, cv2.ROTATE_180) # only nessecary if camera setup is upside-down
            gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY) # converts image into grayscale
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)

            if len(faces) > 0:
                print("Face detected after motion trigger")
                send_email('Recepient email', 'Doorbell Alert', 'Motion and person detected at door')
            else:
                print("Motion detected, but no face found.")

        cv2.imshow("Door Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if button.is_pressed:
        buzz(200, 2)
        print("doorbell rang")
        send_email( 'Recepient email', 'Doorbell Alert', 'Someone just rang your doorbell')

    sleep(1)

cap.release()
cv2.destroyAllWindows()
