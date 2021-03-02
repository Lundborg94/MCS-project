import sqlite3
from sqlite3 import Error


def create_tables():
    conn = None
    try:
        conn = sqlite3.connect('databases/mcsservice.db')

        # Create User table
        conn.execute("""
            CREATE TABLE User (
                Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Name NVARCHAR NOT NULL,
                Password NVARCHAR NOT NULL
            )
        """)

        # Create Device table
        conn.execute("""
            CREATE TABLE Device (
                Id uuid PRIMARY KEY NOT NULL,
                UserId INTEGER NOT NULL,
                Name NVARCHAR NOT NULL,
                FOREIGN KEY(UserId) REFERENCES User(Id)
            )
        """)

        # Create EmergencyContact table
        conn.execute("""
            CREATE TABLE EmergencyContact (
                Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                DeviceId NVARCHAR NOT NULL,
                PhoneNumber NVARCHAR NOT NULL,
                FOREIGN KEY(DeviceId) REFERENCES Device(Id)
            )
        """)

        conn.commit()

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def populate():
    conn = None
    try:
        conn = sqlite3.connect('databases/mcsservice.db')

        print("Inser into user")
        conn.execute("""
            INSERT INTO User
                VALUES
                    (NULL, 'Äpple Äpplesson', 'Äpplesson123'),
                    (NULL, 'Gurka Gurksson', 'Gurksson123'),
                    (NULL, 'Päron Päronsson', 'Päronsson123')
        """)

        print("Inser into device")
        conn.execute("""
            INSERT INTO Device
                VALUES
                    ('6cc4cf69-843d-407b-9d03-2b70b2efe9c5', 1, 'Motorcykeln'),
                    ('64ef1aad-adc0-4a15-9e02-e752f837a0fe', 1, 'Cykeln'),

                    ('5d634db7-be28-4bce-986a-6426c502428e', 2, 'Mopeden'),
                    ('cb8e0fef-62f0-4c74-8b5e-70abe923feeb', 2, 'Teslan'),
                    ('3e76f96f-5bd1-49e6-85d6-8d34cb124924', 2, 'Båten'),

                    ('af849430-0f28-4e03-b20e-470a62266302', 3, 'Tjänstebilen'),
                    ('680ebc91-4f96-4388-98f5-8a180b4b00c7', 3, 'Fritidsbilen')
        """)

        print("Inser into emergency contact")
        conn.execute("""
            INSERT INTO EmergencyContact
                VALUES
                    (NULL, '6cc4cf69-843d-407b-9d03-2b70b2efe9c5', '+46XXXXXXXX0'),
                    (NULL, '64ef1aad-adc0-4a15-9e02-e752f837a0fe', '+46XXXXXXXX1'),

                    (NULL, '5d634db7-be28-4bce-986a-6426c502428e', '+46XXXXXXXX2'),
                    (NULL, 'cb8e0fef-62f0-4c74-8b5e-70abe923feeb', '+46XXXXXXXX3'),
                    (NULL, 'cb8e0fef-62f0-4c74-8b5e-70abe923feeb', '+46XXXXXXXX4'),
                    (NULL, '3e76f96f-5bd1-49e6-85d6-8d34cb124924', '+46XXXXXXXX5'),
                    
                    (NULL, 'af849430-0f28-4e03-b20e-470a62266302', '+46XXXXXXXX6'),
                    (NULL, 'af849430-0f28-4e03-b20e-470a62266302', '+46XXXXXXXX7'),
                    (NULL, 'af849430-0f28-4e03-b20e-470a62266302', '+46XXXXXXXX8'),
                    (NULL, 'af849430-0f28-4e03-b20e-470a62266302', '+46XXXXXXXX9'),
                    (NULL, '680ebc91-4f96-4388-98f5-8a180b4b00c7', '+46XXXXXXX10')               
        """)

        conn.commit()

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    create_tables()
    populate()
