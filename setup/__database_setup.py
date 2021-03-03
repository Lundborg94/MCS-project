import sqlite3
from sqlite3 import Error


def create_tables():
    conn = None
    try:
        conn = sqlite3.connect('deviceservice.db')

        # Create Device table
        conn.execute("""
            CREATE TABLE Device (
                Id uuid PRIMARY KEY NOT NULL,
                Name NVARCHAR NOT NULL,
                Password NVARCHAR NOT NULL
            )
        """)

        # Create EmergencyContact table
        conn.execute("""
            CREATE TABLE EmergencyContact (
                Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                DeviceId NVARCHAR NOT NULL,
                PhoneNumber NVARCHAR NOT NULL,
                
                CONSTRAINT fk_Device
                    FOREIGN KEY(DeviceId)
                    REFERENCES Device(Id)
                    ON DELETE CASCADE
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
        conn = sqlite3.connect('deviceservice.db')

        conn.execute('PRAGMA foreign_keys = ON')

        conn.execute("""
            INSERT INTO Device
                VALUES
                    ('6cc4cf69-843d-407b-9d03-2b70b2efe9c5', 'Motorcykeln', 'Äpple123'),
                    ('64ef1aad-adc0-4a15-9e02-e752f837a0fe', 'Cykeln', 'Gurka123'),
                    ('5d634db7-be28-4bce-986a-6426c502428e', 'Mopeden', 'Päron123'),
                    ('cb8e0fef-62f0-4c74-8b5e-70abe923feeb', 'Teslan', 'Kaffe123'),
                    ('3e76f96f-5bd1-49e6-85d6-8d34cb124924', 'Båten', 'Tårta123'),
                    ('af849430-0f28-4e03-b20e-470a62266302', 'Tjänstebilen', 'Anannas123'),
                    ('680ebc91-4f96-4388-98f5-8a180b4b00c7', 'Fritidsbilen', 'Kiwi123')
        """)

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


def main():
    create_tables()
    populate()


if __name__ == '__main__':
    main()
