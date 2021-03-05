import sqlite3
import uuid
import datetime
import cumulocity_api


# ENTITIES
class EmergencyContact:
    def __init__(self, id, device_id: uuid, phone_number: str):
        self.id = id
        self.device_id = device_id
        self.phone_number = phone_number


class Device:
    def __init__(self, id: uuid, name: str, password: str):
        self.id = id
        self.name = name
        self.password = password


# INTERFACES
class DeviceRepositoryInterface:
    """
    Device repository interface.
    All adaptors should inherit this class.
    """

    def get_device(self, id: uuid) -> Device:
        """Fetches a device with the specified id from current context"""
        raise NotImplementedError()

    def add_device(self, id: uuid, name: str, password):
        """Adds a device to current context"""
        raise NotImplementedError()

    def remove_device(self, id: uuid):
        """Removes a device from the current context"""
        raise NotImplementedError()


class EmergencyRepositoryInterface:

    def get_emergency_contact(self, id):
        """Fetches an emergency contact from the current context"""
        raise NotImplementedError()

    def get_emergency_contacts_for_device(self, device_id: uuid):
        """Fetches emergency contacts for specified device"""
        raise NotImplementedError()

    def add_emergency_contact(self, device_id: uuid, phone_number: str):
        """Adds an emergency contact to the current context"""
        raise NotImplementedError()

    def remove_emergency_contact(self, id: int):
        """Removes an emergency contact from the current context"""
        raise NotImplementedError()


# ADAPTORS
class DeviceRepositoryTest(DeviceRepositoryInterface):
    """
    For testing against our sqlite db
    """

    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__context = sqlite_connection
        self.__context.execute('PRAGMA foreign_keys = ON')  # For cascade deletion and restrictions

    def get_device(self, id: uuid):
        cursor = self.__context.execute('SELECT * FROM Device WHERE Id = ?', [str(id)])

        tup = cursor.fetchone()

        if not tup:
            return None

        device = Device(tup[0], tup[1], tup[2])

        return device

    def add_device(self, id: uuid, name: str, password: str):
        self.__context.execute('INSERT INTO Device VALUES (?, ?, ?, NULL)', [str(id), name, password])
        self.__context.commit()

    def remove_device(self, id: uuid):
        self.__context.execute('DELETE FROM Device WHERE Id = ?', [str(id)])
        self.__context.commit()


class EmergencyRepositoryTest(EmergencyRepositoryInterface):

    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__context = sqlite_connection
        self.__context.execute('PRAGMA foreign_keys = ON')  # For cascade deletion and restrictions

    def get_emergency_contact(self, id):
        cursor = self.__context.execute('SELECT * FROM EmergencyContact WHERE Id = ?', [id])
        tup = cursor.fetchone()
        ec = EmergencyContact(tup[0], tup[1], tup[2])
        return ec

    def get_emergency_contacts_for_device(self, device_id: uuid) -> list[EmergencyContact]:
        cursor = self.__context.execute('SELECT * FROM EmergencyContact WHERE DeviceId = ?', [device_id])
        tups = cursor.fetchall()
        return [EmergencyContact(tup[0], tup[1], tup[2]) for tup in tups]

    def add_emergency_contact(self, device_id: uuid, phone_number: str):
        self.__context.execute('INSERT INTO EmergencyContact VALUES (?, ?, ?)', [None, str(device_id), phone_number])
        self.__context.commit()

    def remove_emergency_contact(self, id: int):
        self.__context.execute('DELETE FROM EmergencyContact WHERE Id = ?', [id])
        self.__context.commit()


class CumulocityRepository:

    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__context = sqlite_connection
        self.__context.execute('PRAGMA foreign_keys = ON')  # For cascade deletion and restrictions

    def get_active_cumulocity_device(self):
        cursor = self.__context.execute("""
            SELECT
                d.Id,
                c.Username,
                c.TenantId,
                c.Password
            FROM Device d
            JOIN Cumulocity c ON d.CumulocityId = c.Id
            WHERE c.Active == 1
        """)

        return cursor.fetchall()

    def add_cumulocity(self, cumulocity_username, cumulocity_tenant_id, cumulocity_password, user_id, active):
        self.__context.execute('INSERT INTO Cumulocity VALUES (null, ?, ?, ?, ?)', [cumulocity_username, cumulocity_tenant_id, cumulocity_password, active])
        self.__context.commit()
        cursor = self.__context.execute('SELECT Id FROM Cumulocity WHERE TenantId = ? AND Password = ?', [cumulocity_tenant_id, cumulocity_password])
        cumulocity_id, = cursor.fetchone()
        self.__context.execute('UPDATE Device SET CumulocityId = ? WHERE Id = ?', [cumulocity_id, user_id])
        self.__context.commit()

    def get_realtime_location(self, device_id):
        context = self.__context.execute("""
            SELECT
                c.Username,
                c.TenantId,
                c.Password
            FROM Device d
            JOIN Cumulocity c on d.CumulocityId = c.Id
            WHERE d.Id = ?
        """, [str(device_id)])

        username, tenant_id, password = context.fetchone()

        return cumulocity_api.get_location(username, tenant_id, password)


class LocationRepository:

    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__context = sqlite_connection
        self.__context.execute('PRAGMA foreign_keys = ON')

    def add_location(self, device_id, latitude, longitude, altitude):
        self.__context.execute('INSERT INTO Position VALUES (NULL, ?, ?, ?, ?, ?)', [str(device_id), latitude, longitude, altitude, datetime.datetime.utcnow()])
        self.__context.commit()

    def get_latest_location(self, device_id):
        cursor = self.__context.execute("""
            SELECT
                p.Latitude,
                p.Longitude,
                p.Altitude,
                p.CreatedDateTime
            FROM Position p
            WHERE p.DeviceId = ?
            ORDER BY p.CreatedDateTime DESC
            LIMIT 1
        """, [str(device_id)])

        tup = cursor.fetchone()

        if not tup:
            return None

        return {
            "latitude": tup[0],
            "longitude": tup[1],
            "altitude": tup[2],
            "date_time": tup[3]
        }
