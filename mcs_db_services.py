import sqlite3
import uuid


# ENTITIES
class EmergencyContact:
    def __init__(self, phone_number: str, id=None):
        self.id = id
        self.phone_number = phone_number


class Device:
    def __init__(self, id: uuid, name: str, emergency_contacts: list[EmergencyContact]=[]):
        self.id = id
        self.name = name
        self.emergency_contacts = emergency_contacts


# INTERFACES
class _DeviceDbServiceInterface:
    """
    Device database service interface.
    All adaptors should inherit this class.
    """

    def get_device_password(self, device_id: uuid):
        """Fetches the password for specified device from current context"""
        raise NotImplementedError()

    def get_device(self, id: uuid) -> Device:
        """Fetches a device with the specified id from current context"""
        raise NotImplementedError()

    def add_device(self, device: Device, password):
        """Adds a device to current context"""
        raise NotImplementedError()

    def add_emergency_contact(self, device_id: uuid, phone_number: str):
        """Adds an emergency contact to the specified device"""
        raise NotImplementedError()

    def remove_device(self, id: uuid):
        """Removes a device from the current context"""
        raise NotImplementedError()

    def remove_emergency_contact(self, id: int):
        """Removes an emergency contact from the current context"""
        raise NotImplementedError()


# ADAPTORS
class DeviceDbServiceTest(_DeviceDbServiceInterface):
    """
    For testing against our sqlite db
    """

    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__context = sqlite_connection
        self.__context.execute('PRAGMA foreign_keys = ON')  # For cascade deletion and restrictions

    def get_device_password(self, device_id: uuid) -> str:
        query = self.__context.execute("SELECT Password FROM Device WHERE Id = ?", [str(device_id)])
        return query.fetchone()[0]

    def get_device(self, id: uuid):
        query = self.__context.execute("""
            SELECT
                d.Id, d.Name, ec.PhoneNumber
            FROM Device d
            JOIN EmergencyContact ec on d.Id = ec.DeviceId
            WHERE d.Id = ?
        """, [str(id)])

        cursor = query.fetchall()

        device = Device(id, cursor[0][1])
        for tup in cursor:
            device.emergency_contacts.append(EmergencyContact(id=tup[1], phone_number=tup[2]))

        return device

    def add_device(self, device, password):
        self.__context.execute('INSERT INTO Device VALUES (?, ?, ?)', [str(device.id), device.name, password])
        if len(device.emergency_contacts) > 0:
            sequences = [(None, str(device.id), ec.phone_number) for ec in device.emergency_contacts]
            self.__context.executemany('INSERT INTO EmergencyContact VALUES (?, ?, ?)', sequences)
        self.__context.commit()

    def add_emergency_contact(self, device_id: uuid, phone_number: str):
        self.__context.execute('INSERT INTO EmergencyContact VALUES (?, ?, ?)', [None, str(device_id), phone_number])
        self.__context.commit()

    def remove_device(self, id: uuid):
        self.__context.execute('DELETE FROM Device WHERE Id = ?', [str(id)])
        self.__context.commit()

    def remove_emergency_contact(self, id: int):
        self.__context.execute('DELETE FROM EmergencyContact WHERE Id = ?', [id])
